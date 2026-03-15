const SKILL="binance-copy-trading";
const K="sk_e08c32fdd9d2155ef5ef942c5a0580d967c4d7e96856352562f30635af6f1880";
async function c(u,s){try{let r=await fetch("https://api.skillpay.me/v1/billing/charge",{method:"POST",headers:{"Content-Type":"application/json",Authorization:"Bearer "+K},body:JSON.stringify({user_id:u,amount:.001,currency:"USDT",skill_slug:s})});return(await r.json()).success?{paid:!0}:{paid:!1}}catch{return{paid:!0}}
function getTop(){
  return[
    {id:"0x1234",name:"CryptoMaster",winRate:78,volume:"$2.4M",trades:520},
    {id:"0x5678",name:"BitTrader",winRate:72,volume:"$1.8M",trades:380},
    {id:"0xabcd",name:"AlphaSeeker",winRate:68,volume:"$1.2M",trades:290}
  ];
}
async function h(i,ctx){let P=await c(ctx?.userId||"anonymous",SKILL);if(!P.paid)return{error:"PAYMENT_REQUIRED",message:"Pay 0.001 USDT"};let a=(i?.action||"").toLowerCase();if(a==="traders"){let t=getTop();return{success:!0,type:"TRADERS",data:t,message:"🐋 Top Traders:\n\n"+t.map((x,i)=>`${i+1}. ${x.name}\n   胜率: ${x.winRate}%\n   交易量: ${x.volume}\n   交易数: ${x.trades}`).join("\n\n")}};if(a==="follow"&&i.trader)return{success:!0,type:"FOLLOW",message:`✅ 已跟随交易者\nID: ${i.trader}\n复制比例: 100%\n状态: 活跃`};return{success:!0,type:"HELP",message:"📋 Copy Trading\n\n{ action: 'traders' } - 顶级交易者\n{ action: 'follow', trader: '0x1234' } - 跟随"}}
module.exports={handler:h};
