<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>포레스트핏 상품 발주 자동 계산</title>
<script src="https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js"></script>
<style>
*{box-sizing:border-box;font-family:Pretendard,-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic",sans-serif}
body{margin:0;background:#f6f7f6;color:#1f2923}
.wrap{max-width:1180px;margin:0 auto;padding:38px 22px 64px}
.top{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px}
.logo{font-size:20px;font-weight:900;letter-spacing:.08em;color:#244734}
.badge{font-size:12px;font-weight:800;color:#486052;background:#fff;border:1px solid #e3e8e5;padding:8px 13px;border-radius:999px}
h1{font-size:32px;letter-spacing:-.05em;margin:0 0 8px;color:#173d2b}
.desc{font-size:14px;line-height:1.65;color:#6d776f;margin-bottom:20px;font-weight:600}
.card{background:#fff;border:1px solid #e5eae7;border-radius:18px;padding:20px;margin-bottom:14px;box-shadow:0 8px 24px rgba(38,49,43,.045)}
.step-title{display:flex;align-items:center;gap:9px;font-size:16px;font-weight:900;color:#173d2b;margin-bottom:13px}
.step-no{display:inline-flex;align-items:center;justify-content:center;width:27px;height:27px;border-radius:50%;background:#244734;color:#fff;font-size:12px;font-weight:900;flex:0 0 auto}
.drop-zone{border:2px dashed #bfd0c7;border-radius:14px;padding:23px 16px;text-align:center;background:#fbfdfc;transition:.18s ease;cursor:pointer}
.drop-zone.dragover{border-color:#244734;background:#eef7f1;box-shadow:0 0 0 3px rgba(36,71,52,.08)}
.drop-zone input{display:none}
.upload-main{font-size:14px;font-weight:900;color:#244734;margin-bottom:4px}
.upload-sub{font-size:12px;color:#718078;font-weight:650;line-height:1.5}
.file-info{display:none;margin-top:10px;padding:10px 13px;border-radius:11px;background:#eef7f1;color:#244734;font-size:12px;font-weight:800}
.error{display:none;margin-top:10px;padding:10px 13px;border-radius:11px;background:#fff0f0;color:#8a3333;font-size:12px;font-weight:800;white-space:pre-line}
.locked{display:none}
.summary-grid{display:grid;grid-template-columns:1.15fr 2.2fr repeat(3,.72fr);gap:10px}
.summary{border:1px solid #e4e9e6;border-radius:14px;padding:14px;background:#fbfdfc;min-width:0}
.summary .label{font-size:11px;color:#758078;font-weight:750;margin-bottom:6px}
.summary .value{font-size:20px;font-weight:900;color:#244734;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.summary .value.text{font-size:13px;line-height:1.4}
.summary.product-focus{background:#eef7f1;border:2px solid #bcd7c5;box-shadow:inset 0 0 0 1px rgba(36,71,52,.05)}
.summary.product-focus .label{color:#244734;font-weight:900;font-size:12px}
.summary.product-focus .value{color:#173d2b}
.summary.product-focus .value.text{font-size:22px;line-height:1.35;font-weight:900}
.option-sections{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:12px}
.option-box{border:1px solid #e4e9e6;border-radius:14px;padding:14px;background:#fff}
.option-box h3{font-size:12px;margin:0 0 9px;color:#173d2b}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{padding:6px 9px;border-radius:999px;background:#eef5f1;color:#244734;font-size:11px;font-weight:800;border:1px solid #dbe8e1}
.color-setting-grid{display:grid;grid-template-columns:1fr;gap:14px}
.color-setting-card,.result-card{border:1px solid #e1e8e4;border-radius:16px;padding:16px;background:#fbfdfc;min-width:0}
.color-setting-head,.result-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px;flex-wrap:wrap}
.color-name{font-size:16px;font-weight:900;color:#173d2b;min-width:0}
.pill{display:inline-flex;align-items:center;justify-content:center;min-width:78px;padding:7px 10px;border-radius:999px;border:1px solid #dcebe2;background:#eef7f1;color:#1f6c42;font-size:13px;font-weight:900;white-space:nowrap}
.pill.bad{background:#fff0f0;color:#c62828;border-color:#f2b1b1;box-shadow:inset 0 0 0 1px rgba(198,40,40,.08)}
.input-label{font-size:12px;color:#66756d;font-weight:800;margin-bottom:6px}

.input-wrap{display:flex;align-items:center;border:1px solid #d5ded9;border-radius:10px;background:#fff;overflow:hidden;min-width:0}
.input-wrap.qty{
  max-width:240px;
  background:#fff6bf;
  border:2px solid #e3b92f;
  box-shadow:0 0 0 4px rgba(227,185,47,.10);
}
.input-wrap.qty .qty-input{
  background:#fff6bf;
  color:#173d2b;
  font-size:17px;
  font-weight:950;
  padding:11px 8px;
}
.input-wrap.qty .input-unit{
  background:#fff6bf;
  color:#7b5a00;
  font-weight:900;
}
.input-wrap.qty:focus-within{
  border-color:#c88d00;
  box-shadow:0 0 0 4px rgba(200,141,0,.16);
}
.required-badge{
  display:inline-flex;
  align-items:center;
  margin-left:7px;
  padding:3px 7px;
  border-radius:999px;
  background:#fff0cf;
  color:#9a6200;
  border:1px solid #efd28f;
  font-size:10px;
  font-weight:900;
  vertical-align:middle;
}
.num-input{width:100%;min-width:0;border:0;outline:0;padding:9px 5px;text-align:right;font-size:14px;font-weight:900;color:#244734;background:#fff;-moz-appearance:textfield;appearance:textfield}
.num-input::-webkit-outer-spin-button,.num-input::-webkit-inner-spin-button{-webkit-appearance:none;margin:0}
.input-unit{padding:0 7px 0 4px;font-size:11px;font-weight:800;color:#68766f;flex-shrink:0}
.ratio-section{margin-top:15px;padding-top:15px;border-top:1px solid #e4e9e6}
.length-size-list{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:12px}
.length-size-card{border:1px solid #dfe8e3;border-radius:13px;padding:12px;background:#fff;min-width:0}
.length-size-head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:9px}
.length-size-title{font-size:13px;font-weight:900;color:#173d2b}
.length-qty-pill{display:inline-flex;align-items:center;justify-content:center;padding:5px 8px;border-radius:999px;background:#f3f7f5;color:#52675b;font-size:11px;font-weight:850;border:1px solid #e0e8e3;white-space:nowrap}
.length-size-card .ratio-grid{grid-template-columns:repeat(5,minmax(0,1fr));gap:6px}
.length-size-card .ratio-item{padding:8px 5px}
.length-size-card .num-input{font-size:13px;padding:8px 4px}
.length-size-card .input-unit{font-size:10px;padding:0 5px 0 2px}
.length-size-card .ratio-summary{margin-top:9px}
@media(max-width:1050px){.length-size-list{grid-template-columns:1fr}}
.ratio-section-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:9px;flex-wrap:wrap}
.ratio-title{font-size:12px;font-weight:900;color:#173d2b}
.ratio-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}
.length-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.ratio-item{border:1px solid #e4e9e6;border-radius:11px;padding:9px 7px;background:#fff;min-width:0}
.ratio-item .ratio-label{font-size:11px;color:#173d2b;font-weight:900;margin-bottom:7px;text-align:center;white-space:nowrap}
.ratio-summary{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:12px;flex-wrap:wrap}
.summary-caption{font-size:11px;color:#6d776f;font-weight:800;line-height:1.45}
.btn{border:0;border-radius:10px;cursor:pointer;font-weight:900;transition:.15s ease}
.btn:hover:not(:disabled){transform:translateY(-1px)}
.btn:disabled{opacity:.45;cursor:not-allowed}
.btn-reset-row{padding:10px 12px;background:#244734;color:#fff;font-size:11px;box-shadow:0 4px 12px rgba(36,71,52,.14)}
.btn-reset-all{padding:12px 18px;background:#173d2b;color:#fff;font-size:13px;box-shadow:0 6px 16px rgba(23,61,43,.18)}
.card-foot{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:14px;flex-wrap:wrap}
.help-text{font-size:12px;color:#6d776f;font-weight:750;line-height:1.55}
.warn-text{color:#c62828;font-weight:900}
.result-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.result-matrix{width:100%;border-collapse:collapse;table-layout:fixed}
.result-matrix th,.result-matrix td{border-bottom:1px solid #e9efec;border-right:1px solid #eef2f0;padding:9px 6px;text-align:center;font-size:12px}
.result-matrix th:last-child,.result-matrix td:last-child{border-right:0}
.result-matrix thead th{background:#f1f7f3;color:#244734;font-weight:900}
.result-matrix tbody th{background:#fafcfb;color:#5d6e64;font-weight:900;text-align:left;padding-left:10px}
.result-matrix tbody td{color:#173d2b;font-weight:900}
.result-matrix tfoot th,.result-matrix tfoot td{background:#eef5f1;color:#173d2b;font-weight:900;border-bottom:0}
.result-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.mini-pill{display:inline-flex;align-items:center;justify-content:center;padding:6px 10px;border-radius:999px;background:#eef5f1;color:#244734;font-size:12px;font-weight:900;border:1px solid #dce7e1}
.small-note{font-size:11px;color:#7a867f;font-weight:700;margin-top:10px;line-height:1.5}
.download-card{border:2px solid #bfd7c8;background:#f8fcf9}
.download-box{display:flex;align-items:center;justify-content:space-between;gap:18px;flex-wrap:wrap}
.download-actions{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end}
.download-copy{min-width:240px;flex:1}
.download-title{font-size:18px;font-weight:900;color:#173d2b;margin-bottom:5px}
.download-desc{font-size:12px;color:#66756d;font-weight:750;line-height:1.55}
.download-btn{min-width:245px;padding:15px 20px;background:#173d2b;color:#fff;font-size:14px;box-shadow:0 7px 18px rgba(23,61,43,.2)}
.download-status{display:none;margin-top:12px;padding:11px 13px;border-radius:11px;background:#eef7f1;color:#244734;font-size:12px;font-weight:850}
.download-status.bad{background:#fff0f0;color:#a12f2f}
@media(max-width:1050px){
  .color-setting-grid,.result-grid{grid-template-columns:1fr}
}
@media(max-width:900px){
  .summary-grid{grid-template-columns:repeat(2,1fr)}
  .option-sections{grid-template-columns:1fr}
}
@media(max-width:720px){
  .wrap{padding:26px 14px 44px}
  h1{font-size:28px}
  .summary-grid{grid-template-columns:1fr}
  .ratio-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
  .length-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
  .download-actions{width:100%}
  .download-btn{width:100%;min-width:0}
}
</style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <div class="logo">FORESTFIT</div>
    <div class="badge">상품 발주 자동 계산</div>
  </div>

  <h1>상품 옵션 불러오기</h1>
  <div class="desc">셀메이트 상품 다운로드 CSV를 첨부하면 S열 「옵션명」에서 색상 · 기장 · 사이즈를 자동으로 불러옵니다.</div>

  <section class="card">
    <div class="step-title"><span class="step-no">1</span>셀메이트 상품 파일 첨부</div>
    <div id="dropZone" class="drop-zone" role="button" tabindex="0">
      <input type="file" id="fileInput" accept=".csv" />
      <div class="upload-main">CSV 파일을 끌어놓거나 클릭하여 첨부</div>
      <div class="upload-sub">S열 옵션명을 자동으로 읽습니다.</div>
    </div>
    <div id="fileInfo" class="file-info"></div>
    <div id="error" class="error"></div>
  </section>

  <section class="card locked" id="summaryCard">
    <div class="step-title"><span class="step-no">2</span>상품 및 옵션</div>
    <div class="summary-grid">
      <div class="summary"><div class="label">상품코드</div><div class="value text" id="productCode">-</div></div>
      <div class="summary product-focus"><div class="label">현재 발주 설정 상품</div><div class="value text" id="productName">-</div></div>
      <div class="summary"><div class="label">색상</div><div class="value" id="colorCount">0</div></div>
      <div class="summary"><div class="label">기장</div><div class="value" id="lengthCount">0</div></div>
      <div class="summary"><div class="label">사이즈</div><div class="value" id="sizeCount">0</div></div>
    </div>

    <div class="option-sections">
      <div class="option-box"><h3>색상</h3><div class="chips" id="colorChips"></div></div>
      <div class="option-box"><h3>기장</h3><div class="chips" id="lengthChips"></div></div>
      <div class="option-box"><h3>사이즈</h3><div class="chips" id="sizeChips"></div></div>
    </div>
  </section>

  <section class="card locked" id="ratioCard">
    <div class="step-title"><span class="step-no">3</span>색상별 수량 · 기장별 사이즈 비율 설정</div>
    <div id="colorSettingGrid" class="color-setting-grid"></div>
    <div class="card-foot">
      <div class="help-text">
        색상별 수량을 기준으로 <b>각 기장마다 S / M / L / XL / 2XL 비율을 따로 설정</b>할 수 있습니다.<br>
        수량·비율은 비워두거나 <b>0%</b>로 설정해도 다운로드 가능하며, <b>미입력 값은 0장</b>으로 계산합니다. 비율 합계가 100%가 아니면 확인용으로 붉은색 표시만 됩니다.
      </div>
      <button id="resetAllRatios" class="btn btn-reset-all" type="button">전체 기장·사이즈 권장비율 적용</button>
    </div>
  </section>

  <section class="card locked" id="resultCard">
    <div class="step-title"><span class="step-no">4</span>색상 · 사이즈 · 기장별 수량 결과</div>
    <div id="resultGrid" class="result-grid"></div>
    <div class="small-note">* 색상별 수량을 각 기장의 계산 기준으로 사용합니다. 비율이 비어 있거나 0%인 사이즈는 0장으로 계산하며, 비율 합계가 100%가 아니어도 입력한 비율 그대로 계산·다운로드됩니다.</div>
  </section>

  <section class="card download-card locked" id="downloadCard">
    <div class="step-title"><span class="step-no">5</span>엑셀 다운로드</div>
    <div class="download-box">
      <div class="download-copy">
        <div class="download-title">발주 수량 · 발주서 양식 다운로드</div>
        <div class="download-desc">발주 수량은 첨부 엑셀의 첫 번째 탭 양식과 수식을 그대로 사용하여 탭명을 <b>SEET1</b>로 생성하고, 발주서는 두 번째 탭 양식을 유지하여 <b>1.발주서</b>로 생성합니다.</div>
      </div>
      <div class="download-actions">
        <button id="downloadQtyBtn" class="btn download-btn" type="button">발주 수량 Excel 다운로드</button>
        <button id="downloadOrderBtn" class="btn download-btn" type="button">발주서 양식 다운로드</button>
      </div>
    </div>
    <div id="downloadStatus" class="download-status"></div>
  </section>
</div>

<script>
const SIZE_ORDER=['S','M','L','XL','2XL'];
const TEMPLATE_LENGTH_ORDER=['숏','기본','롱'];
const DEFAULT_SIZE_RATIOS={S:15,M:35,L:30,XL:15,'2XL':5};
const TEMPLATE_XLSX_BASE64='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';

const fileInput=document.getElementById('fileInput');
const dropZone=document.getElementById('dropZone');
const errorEl=document.getElementById('error');
const downloadQtyBtn=document.getElementById('downloadQtyBtn');
const downloadBtn=document.getElementById('downloadOrderBtn');

window.forestfitOrderState={
  productCode:'',productName:'',supplier:'',purchaseName:'',cost:0,
  colors:[],lengths:[],normalizedLengths:[],sizes:[],options:[],
  purchaseCodeByColor:{},sizeRatiosByColorLength:{},quantityByColor:{},matricesByColor:{}
};

function showError(msg){errorEl.style.display='block';errorEl.textContent=msg;}
function clearError(){errorEl.style.display='none';errorEl.textContent='';}
function showDownloadStatus(msg,bad=false){
  const el=document.getElementById('downloadStatus');
  el.style.display='block';el.textContent=msg;el.classList.toggle('bad',!!bad);
}
function escapeHtml(v){return String(v??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');}
function cleanCellmateValue(v){
  let s=String(v??'').trim();
  const m=s.match(/^=\s*"([\s\S]*)"$/);
  if(m)s=m[1].replace(/""/g,'"');
  return s.trim();
}
function parseCsv(text){
  const rows=[];let row=[];let field='';let quoted=false;
  for(let i=0;i<text.length;i++){
    const ch=text[i];
    if(quoted){
      if(ch==='"'&&text[i+1]==='"'){field+='"';i++;}
      else if(ch==='"')quoted=false;
      else field+=ch;
    }else{
      if(ch==='"')quoted=true;
      else if(ch===','){row.push(field);field='';}
      else if(ch==='\n'){row.push(field.replace(/\r$/,''));rows.push(row);row=[];field='';}
      else field+=ch;
    }
  }
  if(field.length||row.length){row.push(field.replace(/\r$/,''));rows.push(row);}
  return rows.filter(r=>r.some(v=>String(v).trim()!==''));
}
function decodeCsv(buffer){
  const bytes=new Uint8Array(buffer);let kr='';let utf='';
  try{kr=new TextDecoder('euc-kr').decode(bytes);}catch(e){}
  try{utf=new TextDecoder('utf-8').decode(bytes);}catch(e){}
  const bad=s=>(s.match(/�/g)||[]).length;
  return bad(kr)<=bad(utf)?kr:utf;
}
function uniqueKeepOrder(arr){const seen=new Set(),out=[];arr.forEach(v=>{if(v!==''&&!seen.has(v)){seen.add(v);out.push(v);}});return out;}
function sortSizes(values){const unique=uniqueKeepOrder(values);return [...SIZE_ORDER.filter(s=>unique.includes(s)),...unique.filter(s=>!SIZE_ORDER.includes(s))];}
function normalizeLength(v){
  const s=String(v||'').trim().toUpperCase();
  if(!s||s==='일반'||s==='단일기장'||s==='BASIC')return '기본';
  if(s==='숏'||s==='SHORT')return '숏';
  if(s==='기본')return '기본';
  if(s==='롱'||s==='LONG')return '롱';
  return String(v||'').trim();
}
function parseOption(optionName){
  const tokens=String(optionName||'').split(',').map(v=>v.trim()).filter(Boolean);
  if(!tokens.length)return {color:'',length:'',size:''};
  const size=tokens[tokens.length-1]||'';
  if(tokens.length>=3)return {color:tokens.slice(0,-2).join(','),length:tokens[tokens.length-2],size};
  if(tokens.length===2)return {color:tokens[0],length:'기본',size};
  return {color:tokens[0],length:'기본',size:''};
}
function renderChips(id,values){document.getElementById(id).innerHTML=values.map(v=>`<span class="chip">${escapeHtml(v)}</span>`).join('')||'<span class="chip">없음</span>';}
function safeNumber(value){const n=Number(value);return Number.isFinite(n)&&n>=0?n:0;}
function ratioSum(map,keys){return keys.reduce((sum,key)=>sum+safeNumber(map?.[key]),0);}
function equalRatios(keys){
  const result={};if(!keys.length)return result;
  const base=Math.floor(100/keys.length);let rem=100-base*keys.length;
  keys.forEach(key=>{result[key]=base;});
  // 가운데 기장이 있으면 나머지를 기본에 먼저 배정
  const preferred=keys.includes('기본')?'기본':keys[0];
  if(rem>0){result[preferred]+=1;rem--;}
  for(const key of keys){if(rem<=0)break;result[key]+=1;rem--;}
  return result;
}
function allocateByKeys(totalQty,ratioMap,keys){
  const total=Math.round(safeNumber(totalQty));
  const out={};keys.forEach(k=>out[k]=0);
  if(total<=0||!keys.length)return out;

  const sum=ratioSum(ratioMap,keys);
  const exacts=keys.map((key,index)=>({
    key,index,exact:total*safeNumber(ratioMap?.[key])/100
  }));

  // 비율 합계가 정확히 100%이면 반올림 오차를 보정해 배분합계가 기준 수량과 같도록 합니다.
  if(Math.abs(sum-100)<=0.000001){
    let used=0;
    exacts.forEach(x=>{out[x.key]=Math.floor(x.exact);used+=out[x.key];});
    let rem=total-used;
    exacts.map(x=>({...x,frac:x.exact-Math.floor(x.exact)}))
      .sort((a,b)=>b.frac-a.frac||a.index-b.index)
      .forEach(x=>{if(rem>0){out[x.key]++;rem--;}});
    return out;
  }

  // 100%가 아니어도 다운로드/계산 가능:
  // 각 입력 비율을 그대로 적용하며, 빈칸/0%는 0장으로 계산합니다.
  exacts.forEach(x=>{out[x.key]=Math.round(x.exact);});
  return out;
}
function buildMatrix(color){
  const state=window.forestfitOrderState;
  const baseQty=Math.round(safeNumber(state.quantityByColor[color]));
  const activeLengths=state.normalizedLengths;
  const matrix={};
  const sizeTotals={S:0,M:0,L:0,XL:0,'2XL':0};
  const lengthTotals={숏:0,기본:0,롱:0};
  let total=0;

  SIZE_ORDER.forEach(size=>{matrix[size]={숏:0,기본:0,롱:0,total:0};});

  // 색상별 수량은 각 기장의 공통 계산 기준입니다.
  // 비율이 비어 있거나 0%이면 해당 사이즈 수량은 0장으로 계산합니다.
  activeLengths.forEach(len=>{
    const sizeRatios=state.sizeRatiosByColorLength[color]?.[len]||{};
    const bySize=allocateByKeys(baseQty,sizeRatios,SIZE_ORDER);
    let lengthTotal=0;

    SIZE_ORDER.forEach(size=>{
      const qty=bySize[size]||0;
      if(TEMPLATE_LENGTH_ORDER.includes(len))matrix[size][len]=qty;
      matrix[size].total+=qty;
      sizeTotals[size]+=qty;
      lengthTotal+=qty;
    });

    if(TEMPLATE_LENGTH_ORDER.includes(len)){
      lengthTotals[len]=lengthTotal;
      total+=lengthTotal;
    }
  });

  return {matrix,sizeTotals,lengthTotals,baseQty,total};
}
function getPurchaseCode(value){
  const s=cleanCellmateValue(value);
  if(!s)return '';
  const token=s.split(/\s+/)[0];
  return token||s;
}
function renderColorSettingCards(colors){
  const wrap=document.getElementById('colorSettingGrid');
  const state=window.forestfitOrderState;
  state.sizeRatiosByColorLength={};
  state.quantityByColor={};

  wrap.innerHTML=colors.map((color,colorIndex)=>{
    state.sizeRatiosByColorLength[color]={};
    state.quantityByColor[color]=0;

    const lengthSizeCards=state.normalizedLengths.map((len,lenIndex)=>{
      state.sizeRatiosByColorLength[color][len]={...DEFAULT_SIZE_RATIOS};
      const sizeItems=SIZE_ORDER.map(size=>`<div class="ratio-item"><div class="ratio-label">${size}</div><div class="input-wrap"><input class="num-input length-size-ratio-input" type="number" min="0" step="1" value="${DEFAULT_SIZE_RATIOS[size]}" data-color="${escapeHtml(color)}" data-length="${escapeHtml(len)}" data-size="${size}"><span class="input-unit">%</span></div></div>`).join('');
      return `<div class="length-size-card">
        <div class="length-size-head">
          <div class="length-size-title">${escapeHtml(len)} · 사이즈 비율</div>
          <span class="pill" data-length-size-total="${colorIndex}-${lenIndex}">합계 100%</span>
        </div>
        <div class="length-qty-pill" data-length-qty="${colorIndex}-${lenIndex}">${escapeHtml(len)} 계산 기준 0장</div>
        <div class="ratio-grid" style="margin-top:9px">${sizeItems}</div>
        <div class="ratio-summary">
          <span class="summary-caption">S 15 / M 35 / L 30 / XL 15 / 2XL 5</span>
          <button class="btn btn-reset-row" type="button" data-reset-length-size="${colorIndex}-${lenIndex}">이 기장 권장비율 적용</button>
        </div>
      </div>`;
    }).join('');

    return `<div class="color-setting-card">
      <div class="color-setting-head"><div class="color-name">${escapeHtml(color)}</div><span class="mini-pill">사입명 ${escapeHtml(state.purchaseCodeByColor[color]||'-')}</span></div>
      <div>
        <div class="input-label">색상별 수량 <span class="required-badge">미입력 시 0장</span> <span style="font-weight:700;color:#7a867f">(각 기장에 동일하게 적용)</span></div>
        <div class="input-wrap qty"><input class="num-input qty-input" type="number" min="0" step="1" value="0" data-color="${escapeHtml(color)}"><span class="input-unit">장</span></div>
      </div>
      <div class="ratio-section">
        <div class="ratio-section-head"><div class="ratio-title">기장별 사이즈 비율</div><span class="summary-caption">기장마다 S / M / L / XL / 2XL 비율을 각각 수정할 수 있습니다.</span></div>
        <div class="length-size-list">${lengthSizeCards}</div>
      </div>
    </div>`;
  }).join('');

  wrap.querySelectorAll('.length-size-ratio-input,.qty-input').forEach(el=>el.addEventListener('input',updateAllStates));
  wrap.querySelectorAll('[data-reset-length-size]').forEach(btn=>btn.addEventListener('click',()=>{
    const [colorIndex,lenIndex]=btn.dataset.resetLengthSize.split('-').map(Number);
    resetLengthSizeRatio(colorIndex,lenIndex);
  }));
  updateAllStates();
}
function updateAllStates(){updateStateFromInputs();renderResultCards();updateDownloadButton();}
function updateStateFromInputs(){
  const state=window.forestfitOrderState;
  const sizeByLength={},qty={};

  document.querySelectorAll('.length-size-ratio-input').forEach(input=>{
    const c=input.dataset.color,len=input.dataset.length,size=input.dataset.size;
    if(!sizeByLength[c])sizeByLength[c]={};
    if(!sizeByLength[c][len])sizeByLength[c][len]={};
    sizeByLength[c][len][size]=safeNumber(input.value);
  });
  document.querySelectorAll('.qty-input').forEach(input=>{qty[input.dataset.color]=Math.round(safeNumber(input.value));});

  state.sizeRatiosByColorLength=sizeByLength;
  state.quantityByColor=qty;

  state.colors.forEach((color,colorIndex)=>{
    const baseQty=qty[color]||0;
    state.normalizedLengths.forEach((len,lenIndex)=>{
      const sizeTotal=ratioSum(sizeByLength[color]?.[len]||{},SIZE_ORDER);
      const se=document.querySelector(`[data-length-size-total="${colorIndex}-${lenIndex}"]`);
      if(se){se.textContent=`합계 ${sizeTotal}%`;se.classList.toggle('bad',Math.abs(sizeTotal-100)>0.000001);}
      const qe=document.querySelector(`[data-length-qty="${colorIndex}-${lenIndex}"]`);
      if(qe)qe.textContent=`${len} 계산 기준 ${baseQty.toLocaleString()}장`;
    });
  });
}
function resetLengthSizeRatio(colorIndex,lenIndex){
  const state=window.forestfitOrderState;
  const color=state.colors[colorIndex];
  const len=state.normalizedLengths[lenIndex];
  document.querySelectorAll(`.length-size-ratio-input[data-color="${CSS.escape(color)}"][data-length="${CSS.escape(len)}"]`).forEach(input=>{
    input.value=DEFAULT_SIZE_RATIOS[input.dataset.size]??0;
  });
  updateAllStates();
}
function resetAllRatios(){
  const state=window.forestfitOrderState;
  state.colors.forEach((color,colorIndex)=>{
    state.normalizedLengths.forEach((len,lenIndex)=>{
      document.querySelectorAll(`.length-size-ratio-input[data-color="${CSS.escape(color)}"][data-length="${CSS.escape(len)}"]`).forEach(input=>input.value=DEFAULT_SIZE_RATIOS[input.dataset.size]??0);
    });
  });
  updateAllStates();
}
function renderResultCards(){
  const state=window.forestfitOrderState;const wrap=document.getElementById('resultGrid');
  state.matricesByColor={};
  wrap.innerHTML=state.colors.map(color=>{
    const calc=buildMatrix(color);state.matricesByColor[color]=calc;
    const header=TEMPLATE_LENGTH_ORDER.map(len=>`<th>${len}</th>`).join('');
    const rows=SIZE_ORDER.map(size=>`<tr><th>${size}</th>${TEMPLATE_LENGTH_ORDER.map(len=>`<td>${calc.matrix[size][len]||0}</td>`).join('')}<td>${calc.matrix[size].total||0}</td></tr>`).join('');
    return `<div class="result-card">
      <div class="result-head"><div class="color-name">${escapeHtml(color)}</div><div class="result-meta"><span class="mini-pill">색상별 수량 ${calc.baseQty}장</span><span class="mini-pill">총 발주 ${calc.total}장</span><span class="mini-pill">${escapeHtml(state.purchaseCodeByColor[color]||'-')}</span></div></div>
      <table class="result-matrix"><thead><tr><th>사이즈</th>${header}<th>전체</th></tr></thead><tbody>${rows}</tbody><tfoot><tr><th>합계</th>${TEMPLATE_LENGTH_ORDER.map(len=>`<td>${calc.lengthTotals[len]||0}</td>`).join('')}<td>${calc.total}</td></tr></tfoot></table>
    </div>`;
  }).join('');
}
function validateState(){
  const state=window.forestfitOrderState;const errors=[];
  if(!state.productCode&&!state.productName)errors.push('셀메이트 상품 파일을 먼저 첨부해 주세요.');
  if(state.colors.length>4)errors.push(`고정 발주서 양식은 색상 4개까지 입력할 수 있습니다. 현재 ${state.colors.length}개입니다.`);
  const unsupportedSizes=state.sizes.filter(s=>!SIZE_ORDER.includes(s));
  if(unsupportedSizes.length)errors.push(`발주서 양식에 없는 사이즈가 있습니다: ${unsupportedSizes.join(', ')}`);
  const unsupportedLengths=state.normalizedLengths.filter(l=>!TEMPLATE_LENGTH_ORDER.includes(l));
  if(unsupportedLengths.length)errors.push(`발주서 양식에 없는 기장이 있습니다: ${unsupportedLengths.join(', ')}`);
  // 수량/비율 값은 비어 있거나 0이어도 허용합니다. 미입력 값은 0으로 계산합니다.
  return errors;
}
function validateQuantityState(){
  const state=window.forestfitOrderState;const errors=[];
  if(!state.productCode&&!state.productName)errors.push('셀메이트 상품 파일을 먼저 첨부해 주세요.');
  const unsupportedSizes=state.sizes.filter(s=>!SIZE_ORDER.includes(s));
  if(unsupportedSizes.length)errors.push(`발주 수량 양식에 없는 사이즈가 있습니다: ${unsupportedSizes.join(', ')}`);
  const unsupportedLengths=state.normalizedLengths.filter(l=>!TEMPLATE_LENGTH_ORDER.includes(l));
  if(unsupportedLengths.length)errors.push(`발주 수량 양식에 없는 기장이 있습니다: ${unsupportedLengths.join(', ')}`);
  // 비율 합계가 100%가 아니어도 다운로드 가능합니다.
  return errors;
}
function updateDownloadButton(){
  downloadQtyBtn.disabled=validateQuantityState().length>0;
  downloadBtn.disabled=validateState().length>0;
}

function base64ToUint8Array(b64){const bin=atob(b64);const bytes=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)bytes[i]=bin.charCodeAt(i);return bytes;}
const XML_NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main';
function parseXml(text,label){const doc=new DOMParser().parseFromString(text,'application/xml');const err=doc.getElementsByTagName('parsererror')[0];if(err)throw new Error(`${label} XML 파싱 오류`);return doc;}
function serializeXml(doc){return new XMLSerializer().serializeToString(doc);}
function findCell(doc,ref){return Array.from(doc.getElementsByTagNameNS(XML_NS,'c')).find(c=>(c.getAttribute('r')||'').toUpperCase()===ref.toUpperCase())||null;}
function clearCell(doc,ref){const cell=findCell(doc,ref);if(!cell)return;while(cell.firstChild)cell.removeChild(cell.firstChild);cell.removeAttribute('t');}
function setRowHidden(doc,rowNo,hidden){const row=Array.from(doc.getElementsByTagNameNS(XML_NS,'row')).find(r=>Number(r.getAttribute('r'))===Number(rowNo));if(!row)return;if(hidden){row.setAttribute('hidden','1');}else{row.removeAttribute('hidden');}}
function setCellText(doc,ref,text){const cell=findCell(doc,ref);if(!cell)throw new Error(`${ref} 셀을 찾지 못했습니다.`);while(cell.firstChild)cell.removeChild(cell.firstChild);cell.setAttribute('t','inlineStr');const is=doc.createElementNS(XML_NS,'is');const t=doc.createElementNS(XML_NS,'t');const s=String(text??'');if(/^\s|\s$/.test(s))t.setAttributeNS('http://www.w3.org/XML/1998/namespace','xml:space','preserve');t.textContent=s;is.appendChild(t);cell.appendChild(is);}
function setCellNumber(doc,ref,value){const cell=findCell(doc,ref);if(!cell)throw new Error(`${ref} 셀을 찾지 못했습니다.`);while(cell.firstChild)cell.removeChild(cell.firstChild);cell.removeAttribute('t');const v=doc.createElementNS(XML_NS,'v');v.textContent=String(Number(value)||0);cell.appendChild(v);}
function setCellFormula(doc,ref,formula,cached){const cell=findCell(doc,ref);if(!cell)throw new Error(`${ref} 셀을 찾지 못했습니다.`);while(cell.firstChild)cell.removeChild(cell.firstChild);cell.removeAttribute('t');const f=doc.createElementNS(XML_NS,'f');f.textContent=String(formula||'').replace(/^=/,'');const v=doc.createElementNS(XML_NS,'v');v.textContent=String(Number(cached)||0);cell.appendChild(f);cell.appendChild(v);}
function excelDateSerial(date){return Math.floor((Date.UTC(date.getFullYear(),date.getMonth(),date.getDate())-Date.UTC(1899,11,30))/86400000);}
function updateAppProps(doc){
  const vectors=Array.from(doc.getElementsByTagNameNS('*','vector'));
  vectors.forEach(vec=>{
    const parent=vec.parentNode?.localName;
    if(parent==='HeadingPairs'){
      const i4=Array.from(vec.getElementsByTagNameNS('*','i4'))[0];if(i4)i4.textContent='1';
    }
    if(parent==='TitlesOfParts'){
      vec.setAttribute('size','1');
      const existing=Array.from(vec.childNodes).filter(n=>n.nodeType===1);existing.forEach(n=>vec.removeChild(n));
      const lp=doc.createElementNS('http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes','vt:lpstr');lp.textContent='1.발주서';vec.appendChild(lp);
    }
  });
}
function updateAppPropsWithTitle(doc,title){
  const vectors=Array.from(doc.getElementsByTagNameNS('*','vector'));
  vectors.forEach(vec=>{
    const parent=vec.parentNode?.localName;
    if(parent==='HeadingPairs'){
      const i4=Array.from(vec.getElementsByTagNameNS('*','i4'))[0];if(i4)i4.textContent='1';
    }
    if(parent==='TitlesOfParts'){
      vec.setAttribute('size','1');
      const existing=Array.from(vec.childNodes).filter(n=>n.nodeType===1);existing.forEach(n=>vec.removeChild(n));
      const lp=doc.createElementNS('http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes','vt:lpstr');lp.textContent=title;vec.appendChild(lp);
    }
  });
}
function createCellNode(doc,ref,styleId){
  const cell=doc.createElementNS(XML_NS,'c');cell.setAttribute('r',ref);if(styleId!=null)cell.setAttribute('s',String(styleId));return cell;
}
function setCellNodeText(doc,cell,text){
  while(cell.firstChild)cell.removeChild(cell.firstChild);cell.setAttribute('t','inlineStr');
  const is=doc.createElementNS(XML_NS,'is');const t=doc.createElementNS(XML_NS,'t');const s=String(text??'');
  if(/^\s|\s$/.test(s))t.setAttributeNS('http://www.w3.org/XML/1998/namespace','xml:space','preserve');
  t.textContent=s;is.appendChild(t);cell.appendChild(is);
}
function setCellNodeNumber(doc,cell,value){
  while(cell.firstChild)cell.removeChild(cell.firstChild);cell.removeAttribute('t');const v=doc.createElementNS(XML_NS,'v');v.textContent=String(Number(value)||0);cell.appendChild(v);
}
function setCellNodeFormula(doc,cell,formula,cached){
  while(cell.firstChild)cell.removeChild(cell.firstChild);cell.removeAttribute('t');
  const f=doc.createElementNS(XML_NS,'f');f.textContent=String(formula||'').replace(/^=/,'');
  const v=doc.createElementNS(XML_NS,'v');v.textContent=String(Number(cached)||0);cell.appendChild(f);cell.appendChild(v);
}
function patchQuantitySheet(doc){
  const state=window.forestfitOrderState;
  const colors=state.colors;
  const lengths=state.normalizedLengths.length?state.normalizedLengths:['기본'];
  const sheetData=doc.getElementsByTagNameNS(XML_NS,'sheetData')[0];if(!sheetData)throw new Error('첫 번째 탭의 sheetData를 찾지 못했습니다.');

  // 제목/헤더 행(2~4)은 원본 그대로 유지하고, 데이터 영역(5행 이후)만 사이트 값으로 다시 구성합니다.
  Array.from(sheetData.getElementsByTagNameNS(XML_NS,'row')).forEach(row=>{if(Number(row.getAttribute('r'))>=5)row.parentNode.removeChild(row);});

  const mergeCellsOld=doc.getElementsByTagNameNS(XML_NS,'mergeCells')[0];
  if(mergeCellsOld)mergeCellsOld.parentNode.removeChild(mergeCellsOld);
  const mergeCells=doc.createElementNS(XML_NS,'mergeCells');
  const mergeRefs=[];
  let rowNo=5;

  colors.forEach((color,colorIndex)=>{
    const colorStart=rowNo;
    const baseQty=safeNumber(state.quantityByColor[color]);
    lengths.forEach(len=>{
      const lengthStart=rowNo;
      SIZE_ORDER.forEach((size,sizeIndex)=>{
        const row=doc.createElementNS(XML_NS,'row');row.setAttribute('r',String(rowNo));row.setAttribute('spans','2:7');
        const b=createCellNode(doc,`B${rowNo}`,28);
        const c=createCellNode(doc,`C${rowNo}`,29);
        const d=createCellNode(doc,`D${rowNo}`,29);
        const e=createCellNode(doc,`E${rowNo}`,1);
        const f=createCellNode(doc,`F${rowNo}`,3);
        const g=createCellNode(doc,`G${rowNo}`,1);

        if(rowNo===colorStart){setCellNodeNumber(doc,b,baseQty);setCellNodeNumber(doc,c,colorIndex+1);}
        if(rowNo===lengthStart)setCellNodeText(doc,d,len);
        setCellNodeText(doc,e,size);
        const ratio=safeNumber(state.sizeRatiosByColorLength[color]?.[len]?.[size]);
        setCellNodeNumber(doc,f,ratio/100);
        setCellNodeFormula(doc,g,`$B$${colorStart}*F${rowNo}`,baseQty*ratio/100);
        [b,c,d,e,f,g].forEach(cell=>row.appendChild(cell));sheetData.appendChild(row);
        rowNo++;
      });
      mergeRefs.push(`D${lengthStart}:D${rowNo-1}`);
    });
    mergeRefs.push(`B${colorStart}:B${rowNo-1}`);
    mergeRefs.push(`C${colorStart}:C${rowNo-1}`);
  });

  mergeRefs.forEach(ref=>{const mc=doc.createElementNS(XML_NS,'mergeCell');mc.setAttribute('ref',ref);mergeCells.appendChild(mc);});
  mergeCells.setAttribute('count',String(mergeRefs.length));
  const phonetic=doc.getElementsByTagNameNS(XML_NS,'phoneticPr')[0];
  if(phonetic)phonetic.parentNode.insertBefore(mergeCells,phonetic);else doc.documentElement.appendChild(mergeCells);

  const dimension=doc.getElementsByTagNameNS(XML_NS,'dimension')[0];
  const lastRow=Math.max(4,rowNo-1);if(dimension)dimension.setAttribute('ref',`B2:G${lastRow}`);
}
async function buildQuantityWorkbook(){
  if(typeof JSZip==='undefined')throw new Error('엑셀 파일 생성 모듈을 불러오지 못했습니다. 인터넷 연결 후 다시 시도해주세요.');
  const zip=await JSZip.loadAsync(base64ToUint8Array(TEMPLATE_XLSX_BASE64));
  const sheetFile=zip.file('xl/worksheets/sheet1.xml');if(!sheetFile)throw new Error('첫 번째 탭 양식을 찾지 못했습니다.');
  const sheetDoc=parseXml(await sheetFile.async('string'),'발주 수량');patchQuantitySheet(sheetDoc);zip.file('xl/worksheets/sheet1.xml',serializeXml(sheetDoc));

  const workbookDoc=parseXml(await zip.file('xl/workbook.xml').async('string'),'workbook');
  const sheets=Array.from(workbookDoc.getElementsByTagNameNS(XML_NS,'sheet'));
  sheets.forEach(sheet=>{
    const rid=sheet.getAttributeNS('http://schemas.openxmlformats.org/officeDocument/2006/relationships','id')||sheet.getAttribute('r:id');
    if(rid==='rId1'){sheet.setAttribute('name','SEET1');sheet.setAttribute('sheetId','1');}
    else sheet.parentNode.removeChild(sheet);
  });
  const calcPr=workbookDoc.getElementsByTagNameNS(XML_NS,'calcPr')[0];if(calcPr){calcPr.setAttribute('calcMode','auto');calcPr.setAttribute('fullCalcOnLoad','1');calcPr.setAttribute('forceFullCalc','1');}
  zip.file('xl/workbook.xml',serializeXml(workbookDoc));

  const relDoc=parseXml(await zip.file('xl/_rels/workbook.xml.rels').async('string'),'workbook rels');
  Array.from(relDoc.getElementsByTagNameNS('*','Relationship')).forEach(rel=>{if(['rId2','rId6'].includes(rel.getAttribute('Id')))rel.parentNode.removeChild(rel);});
  zip.file('xl/_rels/workbook.xml.rels',serializeXml(relDoc));

  const ctDoc=parseXml(await zip.file('[Content_Types].xml').async('string'),'content types');
  Array.from(ctDoc.getElementsByTagNameNS('*','Override')).forEach(node=>{if(['/xl/worksheets/sheet2.xml','/xl/calcChain.xml'].includes(node.getAttribute('PartName')))node.parentNode.removeChild(node);});
  zip.file('[Content_Types].xml',serializeXml(ctDoc));

  const appFile=zip.file('docProps/app.xml');
  if(appFile){const appDoc=parseXml(await appFile.async('string'),'app props');updateAppPropsWithTitle(appDoc,'프로그래밍 요망');zip.file('docProps/app.xml',serializeXml(appDoc));}
  zip.remove('xl/worksheets/sheet2.xml');zip.remove('xl/calcChain.xml');
  return zip.generateAsync({type:'blob',mimeType:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',compression:'DEFLATE',compressionOptions:{level:6}});
}
async function downloadQuantityWorkbook(){
  const errors=validateQuantityState();
  if(errors.length){showDownloadStatus(errors.join('\n'),true);alert(errors[0]);return;}
  downloadQtyBtn.disabled=true;downloadQtyBtn.textContent='발주 수량 생성 중...';
  showDownloadStatus('첫 번째 탭의 양식과 수식을 유지하면서 현재 색상·기장별 사이즈 비율을 반영하고 있습니다.');
  try{
    const blob=await buildQuantityWorkbook();
    const a=document.createElement('a');const url=URL.createObjectURL(blob);a.href=url;
    const safeCode=(window.forestfitOrderState.productCode||'상품').replace(/[\\/:*?"<>|]/g,'_');
    a.download=`${safeCode}_발주수량.xlsx`;document.body.appendChild(a);a.click();document.body.removeChild(a);setTimeout(()=>URL.revokeObjectURL(url),1500);
    showDownloadStatus('다운로드 완료 · 첫 번째 탭의 양식과 수식을 유지하고 탭명을 SEET1로 생성했습니다.');
  }catch(err){console.error(err);showDownloadStatus(`발주 수량 생성 오류: ${err.message}`,true);alert(`발주 수량 파일 생성 중 오류가 발생했습니다.\n${err.message}`);}
  finally{downloadQtyBtn.disabled=false;downloadQtyBtn.textContent='발주 수량 Excel 다운로드';updateDownloadButton();}
}
function patchTemplateSheet(doc){
  const state=window.forestfitOrderState;
  const colors=state.colors.slice(0,4);
  // 상단 G1:G3은 사용자가 직접 입력할 수 있도록 다운로드 시 비워둡니다.
  // 원본 셀 스타일(fill 없음)은 그대로 유지됩니다.
  clearCell(doc,'G1');
  clearCell(doc,'G2');
  clearCell(doc,'G3');
  setCellText(doc,'C6',state.productName||'');
  setCellText(doc,'C7',state.supplier||'');
  setCellText(doc,'C8',state.purchaseName||'');
  setCellNumber(doc,'C9',state.cost||0);

  const blockHeaderRows=[23,32,41,50];
  const blockSizeStarts=[25,34,43,52];
  const blockTotalRows=[30,39,48,57];
  const lengthCol={숏:'B',기본:'C',롱:'D'};
  let totalQty=0,totalSupply=0,totalVat=0,totalGrand=0;

  for(let i=0;i<4;i++){
    const summaryRow=14+i;
    const color=colors[i];
    const headerRow=blockHeaderRows[i];
    const sizeStart=blockSizeStarts[i];
    const totalRow=blockTotalRows[i];
    if(color){
      setRowHidden(doc,summaryRow,false);
      const calc=buildMatrix(color);const qty=calc.total;const supply=qty*(state.cost||0);const vat=supply*0.1;const grand=supply+vat;
      totalQty+=qty;totalSupply+=supply;totalVat+=vat;totalGrand+=grand;
      const purchaseCode=state.purchaseCodeByColor[color]||'';
      setCellText(doc,`A${summaryRow}`,purchaseCode);
      setCellText(doc,`B${summaryRow}`,color);
      setCellFormula(doc,`C${summaryRow}`,`E${totalRow}`,qty);
      setCellFormula(doc,`D${summaryRow}`,`C${summaryRow}*$C$9`,supply);
      setCellFormula(doc,`E${summaryRow}`,`D${summaryRow}*0.1`,vat);
      setCellFormula(doc,`F${summaryRow}`,`SUM(D${summaryRow}:E${summaryRow})`,grand);
      setCellText(doc,`B${headerRow}`,purchaseCode);
      setCellText(doc,`C${headerRow}`,color);
      SIZE_ORDER.forEach((size,sizeIndex)=>{
        const row=sizeStart+sizeIndex;
        TEMPLATE_LENGTH_ORDER.forEach(len=>{
          const ref=`${lengthCol[len]}${row}`;const value=calc.matrix[size][len]||0;
          setCellNumber(doc,ref,value);
        });
        setCellFormula(doc,`E${row}`,`SUM(B${row}:D${row})`,calc.matrix[size].total||0);
      });
      TEMPLATE_LENGTH_ORDER.forEach(len=>setCellFormula(doc,`${lengthCol[len]}${totalRow}`,`SUM(${lengthCol[len]}${sizeStart}:${lengthCol[len]}${sizeStart+4})`,calc.lengthTotals[len]||0));
      setCellFormula(doc,`E${totalRow}`,`SUM(E${sizeStart}:F${sizeStart+4})`,qty);
    }else{
      // 고정 양식의 행 번호를 직접 삭제하면 아래 세부내역 위치가 바뀌므로,
      // 사용하지 않는 발주 개요 행은 숨겨서 빈 행이 보이거나 인쇄되지 않게 처리합니다.
      setRowHidden(doc,summaryRow,true);
      ['A','B','C','D','E','F','G'].forEach(col=>clearCell(doc,`${col}${summaryRow}`));
      clearCell(doc,`B${headerRow}`);clearCell(doc,`C${headerRow}`);
      SIZE_ORDER.forEach((_,sizeIndex)=>{
        const row=sizeStart+sizeIndex;['B','C','D','E'].forEach(col=>clearCell(doc,`${col}${row}`));
      });
      ['B','C','D','E'].forEach(col=>clearCell(doc,`${col}${totalRow}`));
    }
  }
  setCellFormula(doc,'C18','SUM(C14:C17)',totalQty);
  setCellFormula(doc,'D18','SUM(D14:D17)',totalSupply);
  setCellFormula(doc,'E18','SUM(E14:E17)',totalVat);
  setCellFormula(doc,'F18','SUM(F14:G17)',totalGrand);
}
async function buildOrderWorkbook(){
  if(typeof JSZip==='undefined')throw new Error('엑셀 파일 생성 모듈을 불러오지 못했습니다. 인터넷 연결 후 다시 시도해주세요.');
  const zip=await JSZip.loadAsync(base64ToUint8Array(TEMPLATE_XLSX_BASE64));
  const sheetFile=zip.file('xl/worksheets/sheet2.xml');if(!sheetFile)throw new Error('발주서 양식 탭을 찾지 못했습니다.');
  const sheetDoc=parseXml(await sheetFile.async('string'),'발주서');patchTemplateSheet(sheetDoc);zip.file('xl/worksheets/sheet2.xml',serializeXml(sheetDoc));

  const workbookDoc=parseXml(await zip.file('xl/workbook.xml').async('string'),'workbook');
  const sheets=Array.from(workbookDoc.getElementsByTagNameNS(XML_NS,'sheet'));
  sheets.forEach(sheet=>{
    const rid=sheet.getAttributeNS('http://schemas.openxmlformats.org/officeDocument/2006/relationships','id')||sheet.getAttribute('r:id');
    if(rid==='rId2'){sheet.setAttribute('name','1.발주서');sheet.setAttribute('sheetId','1');}
    else sheet.parentNode.removeChild(sheet);
  });
  const calcPr=workbookDoc.getElementsByTagNameNS(XML_NS,'calcPr')[0];if(calcPr){calcPr.setAttribute('calcMode','auto');calcPr.setAttribute('fullCalcOnLoad','1');calcPr.setAttribute('forceFullCalc','1');}
  zip.file('xl/workbook.xml',serializeXml(workbookDoc));

  const relDoc=parseXml(await zip.file('xl/_rels/workbook.xml.rels').async('string'),'workbook rels');
  Array.from(relDoc.getElementsByTagNameNS('*','Relationship')).forEach(rel=>{if(['rId1','rId6'].includes(rel.getAttribute('Id')))rel.parentNode.removeChild(rel);});
  zip.file('xl/_rels/workbook.xml.rels',serializeXml(relDoc));

  const ctDoc=parseXml(await zip.file('[Content_Types].xml').async('string'),'content types');
  Array.from(ctDoc.getElementsByTagNameNS('*','Override')).forEach(node=>{if(['/xl/worksheets/sheet1.xml','/xl/calcChain.xml'].includes(node.getAttribute('PartName')))node.parentNode.removeChild(node);});
  zip.file('[Content_Types].xml',serializeXml(ctDoc));

  const appFile=zip.file('docProps/app.xml');
  if(appFile){const appDoc=parseXml(await appFile.async('string'),'app props');updateAppProps(appDoc);zip.file('docProps/app.xml',serializeXml(appDoc));}
  zip.remove('xl/worksheets/sheet1.xml');zip.remove('xl/calcChain.xml');
  return zip.generateAsync({type:'blob',mimeType:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',compression:'DEFLATE',compressionOptions:{level:6}});
}
async function downloadOrderWorkbook(){
  const errors=validateState();
  if(errors.length){showDownloadStatus(errors.join('\n'),true);alert(errors[0]);return;}
  downloadBtn.disabled=true;downloadBtn.textContent='발주서 생성 중...';showDownloadStatus('발주서 양식에 상품정보와 색상·기장·사이즈별 계산 수량을 반영하고 있습니다. G1:G3은 비워두고 발주 개요의 빈 행은 숨깁니다.');
  try{
    const blob=await buildOrderWorkbook();
    const a=document.createElement('a');const url=URL.createObjectURL(blob);a.href=url;
    const safeCode=(window.forestfitOrderState.productCode||'상품').replace(/[\\/:*?"<>|]/g,'_');
    a.download=`${safeCode}_발주서.xlsx`;document.body.appendChild(a);a.click();document.body.removeChild(a);setTimeout(()=>URL.revokeObjectURL(url),1500);
    showDownloadStatus('다운로드 완료 · 두 번째 탭 양식을 유지하고 탭 이름을 「1.발주서」로 생성했습니다.');
  }catch(err){console.error(err);showDownloadStatus(`발주서 생성 오류: ${err.message}`,true);alert(`발주서 생성 중 오류가 발생했습니다.\n${err.message}`);}
  finally{downloadBtn.disabled=false;downloadBtn.textContent='발주서 양식 다운로드';updateDownloadButton();}
}
async function handleFile(file){
  if(!file)return;clearError();
  if(!/\.csv$/i.test(file.name)){showError('셀메이트 CSV 파일(.csv)을 첨부해 주세요.');return;}
  try{
    const buffer=await file.arrayBuffer();const text=decodeCsv(buffer);const rows=parseCsv(text);if(rows.length<2)throw new Error('데이터 행을 찾지 못했습니다.');
    const headers=rows[0].map(v=>String(v).trim());const col=name=>headers.findIndex(h=>h===name);
    let optionIdx=col('옵션명');if(optionIdx<0&&headers.length>=19)optionIdx=18;if(optionIdx<0)throw new Error('S열 「옵션명」을 찾지 못했습니다.');
    const pCodeIdx=col('상품코드'),pNameIdx=col('상품명'),supplierIdx=col('공급처'),purchaseIdx=col('사입상품명'),purchaseOptionIdx=col('사입옵션명'),costIdx=col('원가');
    const parsed=[];
    for(let i=1;i<rows.length;i++){
      const option=cleanCellmateValue(rows[i][optionIdx]||'');if(!option)continue;
      const po=parseOption(option);
      parsed.push({...po,option,
        productCode:pCodeIdx>=0?cleanCellmateValue(rows[i][pCodeIdx]||''):'',productName:pNameIdx>=0?cleanCellmateValue(rows[i][pNameIdx]||''):'',
        supplier:supplierIdx>=0?cleanCellmateValue(rows[i][supplierIdx]||''):'',purchaseName:purchaseIdx>=0?cleanCellmateValue(rows[i][purchaseIdx]||''):'',
        purchaseOption:purchaseOptionIdx>=0?cleanCellmateValue(rows[i][purchaseOptionIdx]||''):'',cost:costIdx>=0?safeNumber(cleanCellmateValue(rows[i][costIdx]||'')):0
      });
    }
    if(!parsed.length)throw new Error('S열 옵션명 데이터가 없습니다.');
    const state=window.forestfitOrderState;
    state.productCode=uniqueKeepOrder(parsed.map(x=>x.productCode).filter(Boolean)).join(' / ');
    state.productName=uniqueKeepOrder(parsed.map(x=>x.productName).filter(Boolean)).join(' / ');
    state.supplier=uniqueKeepOrder(parsed.map(x=>x.supplier).filter(Boolean)).join(' / ');
    state.purchaseName=uniqueKeepOrder(parsed.map(x=>x.purchaseName).filter(Boolean)).join(' / ');
    const costs=uniqueKeepOrder(parsed.map(x=>String(x.cost)).filter(x=>x&&x!=='0'));state.cost=costs.length?safeNumber(costs[0]):0;
    state.colors=uniqueKeepOrder(parsed.map(x=>x.color));
    state.lengths=uniqueKeepOrder(parsed.map(x=>x.length));
    state.normalizedLengths=uniqueKeepOrder(parsed.map(x=>normalizeLength(x.length))).sort((a,b)=>TEMPLATE_LENGTH_ORDER.indexOf(a)-TEMPLATE_LENGTH_ORDER.indexOf(b));
    state.sizes=sortSizes(parsed.map(x=>x.size));state.options=parsed;state.purchaseCodeByColor={};
    state.colors.forEach(color=>{
      const candidates=parsed.filter(x=>x.color===color).map(x=>getPurchaseCode(x.purchaseOption)).filter(Boolean);
      state.purchaseCodeByColor[color]=uniqueKeepOrder(candidates)[0]||state.purchaseName||'';
    });
    document.getElementById('fileInfo').style.display='block';document.getElementById('fileInfo').textContent=`${file.name} · 불러오기 완료`;
    document.getElementById('productCode').textContent=state.productCode||'-';document.getElementById('productName').textContent=state.productName||'-';
    document.getElementById('colorCount').textContent=state.colors.length;document.getElementById('lengthCount').textContent=state.normalizedLengths.length;document.getElementById('sizeCount').textContent=state.sizes.length;
    renderChips('colorChips',state.colors);renderChips('lengthChips',state.normalizedLengths);renderChips('sizeChips',state.sizes);renderColorSettingCards(state.colors);
    ['summaryCard','ratioCard','resultCard','downloadCard'].forEach(id=>document.getElementById(id).classList.remove('locked'));
    const validation=validateState();if(validation.length)showError(validation.join('\n'));else clearError();updateDownloadButton();
  }catch(err){console.error(err);showError(`파일 분석 실패: ${err.message}`);}
}

document.getElementById('resetAllRatios').addEventListener('click',resetAllRatios);
downloadQtyBtn.addEventListener('click',downloadQuantityWorkbook);
downloadBtn.addEventListener('click',downloadOrderWorkbook);
fileInput.addEventListener('change',e=>handleFile(e.target.files[0]));
dropZone.addEventListener('click',()=>fileInput.click());
dropZone.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();fileInput.click();}});
['dragenter','dragover'].forEach(type=>dropZone.addEventListener(type,e=>{e.preventDefault();dropZone.classList.add('dragover');}));
['dragleave','drop'].forEach(type=>dropZone.addEventListener(type,e=>{e.preventDefault();dropZone.classList.remove('dragover');}));
dropZone.addEventListener('drop',e=>handleFile(e.dataTransfer.files?.[0]));
</script>
</body>
</html>
