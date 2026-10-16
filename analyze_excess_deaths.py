from pathlib import Path
import sys, json, warnings
import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
CSV=ROOT/'all_weekly_excess_deaths.csv'
if not CSV.exists(): raise FileNotFoundError(f'Missing dataset: {CSV}')
df=pd.read_csv(CSV)
source_rows, source_cols = df.shape
df['start_date']=pd.to_datetime(df.start_date)
df['end_date']=pd.to_datetime(df.end_date)
df['week_start']=pd.to_datetime([f'{int(y)}-W{int(w):02d}-1' for y,w in zip(df.year,df.week)],format='%G-W%V-%u')
df['iso_week']=df.week_start.dt.strftime('%G-W%V')
df['month']=df.week_start.dt.to_period('M').dt.to_timestamp()
national_df=df[df.region.eq(df.country)].copy()
all_expected=[pd.Timestamp.fromisocalendar(y,w,1) for y in [2020,2021] for w in range(1, (53 if y==2020 else 52)+1)]
requested=[pd.Timestamp.fromisocalendar(2020, w,1) for w in range(1,53)]+[pd.Timestamp.fromisocalendar(2021,w,1) for w in range(1,53)]
# Assignment specifies the literal range 2020-W01 through 2021-W52 (104 weeks).
period_df=national_df[national_df.week_start.isin(requested)].copy()
counts=period_df.groupby('country').week_start.nunique()
complete=counts[counts.eq(len(requested))].index.tolist()
panel_df=period_df[period_df.country.isin(complete)].copy()
weekly=panel_df.groupby(['week_start','iso_week'],as_index=False).agg(excess_deaths=('excess_deaths','sum'))
top=weekly.nlargest(3,'excess_deaths').sort_values('week_start')
country_peaks=panel_df.loc[panel_df.groupby('country').excess_deaths.idxmax(),['country','week_start','excess_deaths']].sort_values('excess_deaths',ascending=False)

# Profile and checks
date_mismatch=int((df.start_date != df.week_start).sum())
misaligned_by_country=df.loc[df.start_date.ne(df.week_start)].groupby('country').size().to_dict()
profile={'rows':len(df),'cols':source_cols,'countries':df.country.nunique(),'regions':df.region.nunique(),'earliest_start':str(df.start_date.min().date()),'latest_start':str(df.start_date.max().date()),'earliest_iso_week':df.iso_week.min(),'latest_iso_week':df.iso_week.max(),'subnational_countries':sorted(df.loc[~df.region.eq(df.country),'country'].unique().tolist()),'missing':df.iloc[:,:source_cols].isna().sum().to_dict(),'duplicates_country_region_week':int(df.duplicated(['country','region','year','week']).sum()),'national_rows':len(national_df),'national_countries':national_df.country.nunique(),'iso2020_weeks':int(df.loc[df.year.eq(2020),'week'].nunique()),'source_start_date_vs_iso_monday_mismatches':date_mismatch,'mismatches_by_country':misaligned_by_country,'literal_period_weeks':len(requested),'panel_countries':len(complete),'panel_rows':len(panel_df),'excluded_incomplete':sorted(set(national_df.country)-set(complete)),'panel_countries_list':complete}
profile['deaths_identity_max_abs_error']=float((df.excess_deaths-(df.total_deaths-df.expected_deaths)).abs().max())
(OUT/'data_profile.json').write_text(json.dumps(profile,indent=2))
pd.DataFrame({'dtype':df.dtypes.astype(str),'missing_count':df.isna().sum(),'missing_pct':df.iloc[:,:source_cols].isna().mean()*100}).to_csv(OUT/'data_quality.csv')

sns.set_theme(style='whitegrid',context='notebook')
# Weekly aggregate with top three peaks
fig,ax=plt.subplots(figsize=(12,5.6)); ax.plot(weekly.week_start,weekly.excess_deaths,color='#1d5d78',lw=1.8); ax.axhline(0,color='black',lw=.8)
offsets=[(-55,10),(0,24),(55,10)]
for i,(_,r) in enumerate(top.iterrows()):
 ax.scatter(r.week_start,r.excess_deaths,color='#bd3f42',zorder=5); ax.annotate(f"{r.iso_week}\n{r.excess_deaths:,.0f}",(r.week_start,r.excess_deaths),xytext=offsets[i],textcoords='offset points',ha='center',fontsize=8,arrowprops={'arrowstyle':'-','color':'#666','lw':.7})
ax.set_ylim(top=weekly.excess_deaths.max()*1.20)
ax.set(title=f"Weekly excess deaths, balanced panel ({len(complete)} countries)",xlabel='ISO week',ylabel='Excess deaths (deaths)'); fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(OUT/'weekly_excess_panel.png',dpi=300); plt.close(fig)
# geographically representative percent small multiples
continent_map={'Australia':'Oceania','New Zealand':'Oceania','Japan':'Asia','South Korea':'Asia','South Africa':'Africa','Brazil':'Latin America','Chile':'Latin America','Canada':'North America','United States':'North America','United Kingdom':'Europe','Spain':'Europe','Italy':'Europe','Germany':'Europe','Mexico':'Latin America','Colombia':'Latin America','Argentina':'Latin America'}
available=set(national_df.country.unique()); chosen=[]
for c in ['Australia','Japan','South Africa','Brazil','Chile','Canada','United Kingdom','Spain','Mexico']:
 if c in available: chosen.append(c)
if len(chosen)<6:
 for c in national_df.country.unique():
  if c not in chosen: chosen.append(c)
  if len(chosen)==9: break
chosen=chosen[:9]
fig,axes=plt.subplots(3,3,figsize=(13,9),sharex=True,sharey=True); axes=axes.ravel()
for ax,c in zip(axes,chosen):
 q=panel_df[panel_df.country.eq(c)]; ax.plot(q.week_start,q.excess_deaths_pct_change*100,color='#287c8e',lw=1.05); ax.axhline(0,color='#555',lw=.6); ax.set_title(c,fontsize=10); ax.set_ylabel('% of expected' if ax in axes[::3] else '')
for ax in axes[len(chosen):]: ax.set_visible(False)
fig.suptitle('Weekly excess deaths as a share of expected deaths\nSelected countries; common scale',y=1.01); fig.tight_layout(); fig.savefig(OUT/'country_small_multiples.png',dpi=300,bbox_inches='tight'); plt.close(fig)
# single country choose Brazil if available (coverage adequate)
single='United States' if 'United States' in available else sorted(available)[0]
one=national_df[national_df.country.eq(single)].sort_values('week_start')
fig,ax=plt.subplots(figsize=(12,5)); ax.plot(one.week_start,one.excess_deaths,label='Excess deaths',lw=1.4); ax.plot(one.week_start,one.covid_deaths,label='Reported COVID-19 deaths',lw=1.2); ax.axhline(0,color='black',lw=.7); ax.set(title=f'{single}: weekly excess deaths and reported COVID-19 deaths',xlabel='ISO week',ylabel='Deaths per reporting week'); ax.legend(); fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(OUT/'country_excess_vs_covid.png',dpi=300); plt.close(fig)
# choropleth using geopandas natural earth low-res GeoJSON from public raw dataset
mapped=False; unmatched=[]; mapped_n=0
try:
 import geopandas as gpd
 world=gpd.read_file('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson')
 cum=panel_df.groupby('country',as_index=False).agg(cumulative_excess_deaths=('excess_deaths','sum'),expected=('expected_deaths','sum'),population=('population','last'),weeks=('week_start','nunique'))
 aliases={'United States':'United States of America','Russia':'Russia','South Korea':'South Korea','Czechia':'Czechia','Taiwan':'Taiwan','Iran':'Iran','Vietnam':'Vietnam','Bolivia':'Bolivia','Tanzania':'Tanzania','Syria':'Syria','Moldova':'Moldova','Venezuela':'Venezuela'}
 namecol='ADMIN' if 'ADMIN' in world.columns else 'name'
 world['join_name']=world[namecol]
 world['join_name']=world.join_name.replace({'United States of America':'United States','United Kingdom':'Britain','Czechia':'Czech Republic','Republic of Korea':'South Korea','Dem. Rep. Korea':'North Korea','Czech Republic':'Czechia','Russian Federation':'Russia','Iran (Islamic Republic of)':'Iran','Viet Nam':'Vietnam','Bolivia (Plurinational State of)':'Bolivia','United Republic of Tanzania':'Tanzania','Syrian Arab Republic':'Syria','Republic of Moldova':'Moldova','Venezuela (Bolivarian Republic of)':'Venezuela','Taiwan':'Taiwan','Congo':'Congo','Democratic Republic of the Congo':'Democratic Republic of the Congo'})
 joined=world.merge(cum,left_on='join_name',right_on='country',how='left'); unmatched=sorted(set(cum.country)-set(joined.loc[joined.country.notna(),'country'])); mapped_n=int(joined.cumulative_excess_deaths.notna().sum())
 vmax=max(abs(cum.cumulative_excess_deaths.min()),abs(cum.cumulative_excess_deaths.max()))
 fig,ax=plt.subplots(figsize=(14,7)); joined.plot(column='cumulative_excess_deaths',ax=ax,cmap='RdBu_r',vmin=-vmax,vmax=vmax,missing_kwds={'color':'#e5e5e5','label':'Not in dataset'},legend=True,legend_kwds={'label':'Cumulative excess deaths (2020-W01 to 2021-W52)','shrink':.65}); ax.set_axis_off(); ax.set_title('Cumulative excess deaths by country, 2020-W01–2021-W52\nGray: no matching country observation; Economist data'); fig.tight_layout(); fig.savefig(OUT/'cumulative_excess_map.png',dpi=300); plt.close(fig); mapped=True
 if (OUT/'map_limitation.txt').exists(): (OUT/'map_limitation.txt').unlink()
 cum['per_100k']=cum.cumulative_excess_deaths/cum.population*100000; cum.to_csv(OUT/'cumulative_country.csv',index=False)
except Exception as e:
 (OUT/'map_limitation.txt').write_text(f'Choropleth generation failed: {type(e).__name__}: {e}\n'); cum=panel_df.groupby('country',as_index=False).agg(cumulative_excess_deaths=('excess_deaths','sum'),expected=('expected_deaths','sum'),population=('population','last'),weeks=('week_start','nunique')); cum['per_100k']=cum.cumulative_excess_deaths/cum.population*100000; cum.to_csv(OUT/'cumulative_country.csv',index=False)
# monthly weighted ratio, restricting country-month to full observed periods; Monday assignment
monthly=panel_df.groupby(['country','month'],as_index=False).agg(total_deaths=('total_deaths','sum'),expected_deaths=('expected_deaths','sum'),nweeks=('week_start','nunique'))
monthly['ratio_pct']=(monthly.total_deaths-monthly.expected_deaths)/monthly.expected_deaths*100
pivot=monthly.pivot(index='country',columns='month',values='ratio_pct'); order=cum.sort_values('cumulative_excess_deaths',ascending=False).country.tolist(); pivot=pivot.reindex(order)
fig,ax=plt.subplots(figsize=(16,max(8,len(pivot)*.24))); sns.heatmap(pivot,cmap='RdBu_r',center=0,vmin=-max(abs(np.nanmin(pivot.values)),abs(np.nanmax(pivot.values))),vmax=max(abs(np.nanmin(pivot.values)),abs(np.nanmax(pivot.values))),mask=pivot.isna(),ax=ax,cbar_kws={'label':'Monthly excess / expected deaths (%)'}); ax.set(title='Monthly excess mortality by country (week assigned to month of Monday)',xlabel='Month',ylabel='Country'); ax.set_xticklabels([pd.Timestamp(x).strftime('%b\n%Y') for x in pivot.columns],rotation=0,fontsize=8); fig.tight_layout(); fig.savefig(OUT/'monthly_country_heatmap.png',dpi=300); plt.close(fig)
monthly.to_csv(OUT/'monthly_country.csv',index=False)
# Save calculated result tables
top.to_csv(OUT/'top_weekly_peaks.csv',index=False); country_peaks.to_csv(OUT/'country_peak_weeks.csv',index=False)
pd.DataFrame({'country':chosen}).to_csv(OUT/'small_multiple_countries.csv',index=False)
print(json.dumps({'profile':profile,'top_peaks':top.to_dict('records'),'country':single,'map_available':mapped,'mapped_countries':mapped_n,'unmatched':unmatched,'largest_cumulative':cum.nlargest(5,'cumulative_excess_deaths')[['country','cumulative_excess_deaths','per_100k']].to_dict('records'),'lowest_cumulative':cum.nsmallest(5,'cumulative_excess_deaths')[['country','cumulative_excess_deaths','per_100k']].to_dict('records'),'country_peaks_top':country_peaks.head(8).to_dict('records'),'small_multiples':chosen},default=str,indent=2))
