import sys, re, io, datetime as dt, requests, openpyxl, csv
sys.path.insert(0,'scripts'); sys.path.insert(0,'programa')
from descargar import semana_amm, UA
out=csv.writer(open('explorar/saa_b2.csv','w',newline=''))
out.writerow(['archivo','dias','energia_SAA_B2_MWh','PD_SAA_B2'])
dom=dt.date(2025,12,28)
while dom<=dt.date(2026,9,27):
    anio,sem=semana_amm(dom)
    try:
        t=requests.get(f'https://www.amm.org.gt/pds.php?anio={anio}&fechadomingo={dom:%Y%m%d}&semana={sem:02d}',headers=UA,timeout=60).text
        for u in re.findall(r'href="([^"]+\.xlsx?)"',t):
            b=requests.get(u,headers=UA,timeout=120).content
            wb=openpyxl.load_workbook(io.BytesIO(b),read_only=True,data_only=True)
            rows=list(wb['ENERGIA'].iter_rows(max_col=12,values_only=True))
            hdr=next(i for i,r in enumerate(rows) if any(isinstance(v,dt.datetime) for v in r))
            cols=[j for j,v in enumerate(rows[hdr]) if isinstance(v,dt.datetime)]
            days=[rows[hdr][j].date() for j in cols]
            e=[[round(float(r[j] or 0)) for j in cols] for r in rows if r[1] and str(r[1]).strip().upper()=='SANTA ANA B2']
            pdv=[(r[3],str(r[4])[:10],str(r[5])[:10]) for r in wb['PD'].iter_rows(values_only=True) if r and r[1]=='SAA-B2']
            out.writerow([u.rsplit('/',1)[-1],f'{days[0]}..{days[-1]}',e,pdv])
    except Exception as ex:
        out.writerow([f'sem{sem}',str(dom),'ERROR',str(ex)[:100]])
    dom+=dt.timedelta(days=7)
