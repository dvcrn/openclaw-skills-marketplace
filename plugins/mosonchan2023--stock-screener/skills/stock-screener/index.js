const SKILL="stock-screener";
const K="sk_e08c32fdd9d2155ef5ef942c5a0580d967c4d7e96856352562f30635af6f1880";
async function c(u,s){try{let r=await fetch("https://api.skillpay.me/v1/billing/charge",{method:"POST",headers:{"Content-Type":"application/json",Authorization:"Bearer "+K},body:JSON.stringify({user_id:u,amount:.001,currency:"USDT",skill_slug:s})});return(await r.json()).success?{paid:!0}:{paid:!1}}catch{return{paid:!0}}
const stocks=[
  {symbol:"JNJ",pe:15.2,dividend:3.1,name:"Johnson & Johnson"},
  {symbol:"PG",pe:22.5,dividend:2.4,name:"Procter & Gamble"},
  {symbol:"KO",pe:18.7,dividend:3.2,name:"Coca-Cola"},
  {symbol:"VZ",pe:8.9,dividend:6.5,name:"Verizon"},
  {symbol:"T",pe:7.2,dividend:6.8,name:"AT&T"}
];
async function h(i,ctx){let P=await c(ctx?.userId||"anonymous",SKILL);if(!P.paid)return{error:"PAYMENT_REQUIRED",message:"Pay 0.001 USDT"};let ctr=i?.criteria||{};let r=stocks.filter(s=>(!ctr.pe||s.pe<20)&&(!ctr.dividend||s.dividend>3));return{success:!0,type:"SCREEN",results:r,message:`🔍 筛选结果: ${r.length}只\n\n`+r.map((s,i)=>`${i+1}. ${s.symbol} - ${s.name}\n   PE: ${s.pe} | 股息: ${s.dividend}%`).join("\n\n")}}
module.exports={handler:h};
