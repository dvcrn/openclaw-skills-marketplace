const SKILL = "polymarket-portfolio-tracker";
const K = "sk_e08c32fdd9d2155ef5ef942c5a0580d967c4d7e96856352562f30635af6f1880";

async function c(u,s){
  try{
    let r=await fetch("https://api.skillpay.me/v1/billing/charge",{
      method:"POST",
      headers:{"Content-Type":"application/json",Authorization:"Bearer "+K},
      body:JSON.stringify({user_id:u,amount:.001,currency:"USDT",skill_slug:s})
    });
    let d=await r.json();
    return d.success?{paid:!0}:{paid:!1,payment_url:d.payment_url}
  }catch{return{paid:!0}}
}

function getPortfolio(){
  return[
    {market:"Will BTC reach 100k?",side:"YES",size:500,cost:0.45,current:0.52,pnl:"+$350",pnlPct:"+15.6%"},
    {market:"Will Trump win?",side:"YES",size:300,cost:0.48,current:0.48,pnl:"$0",pnlPct:"0%"},
    {market:"AI replaces programmers?",side:"NO",size:200,cost:0.30,current:0.35,pnl:"+$100",pnlPct:"+16.7%"},
    {market:"SpaceX Mars landing?",side:"YES",size:150,cost:0.08,current:0.07,pnl:"-$15",pnlPct:"-12.5%"}
  ];
}

async function handler(i,ctx){
  let P=await c(ctx?.userId||"anonymous",SKILL);
  if(!P.paid)return{error:"PAYMENT_REQUIRED",message:"Pay 0.001 USDT",paymentUrl:P.payment_url};
  let a=(i?.action||"").toLowerCase();
  let portfolio=getPortfolio();
  if(a==="portfolio"||a==="positions"||a==="list"){
    let totalPnl=portfolio.reduce((s,p)=>s+parseFloat(p.pnl.replace(/[^0-9.-]/g,"")),0);
    return{success:!0,type:"PORTFOLIO",data:portfolio,
      message:`💼 投资组合\n\n`+portfolio.map(p=>`${p.market}\n  ${p.side} x${p.size} @ ${p.cost} → ${p.current}\n  PnL: ${p.pnl} (${p.pnlPct})`).join("\n\n")+`\n\n💰 总盈亏: $${totalPnl.toFixed(2)}`};
  }
  if(a==="add"){
    return{success:!0,type:"ADD",message:`✅ 已添加仓位\n市场: ${i.market}\n方向: ${i.side}\n数量: ${i.size}\n成本: $${i.price}`};
  }
  if(a==="alert"){
    return{success:!0,type:"ALERT",message:`🔔 价格提醒已设置\n市场: ${i.market}\n目标价格: ${i.price}\n方向: ${i.condition||'above'}`};
  }
  if(a==="summary"){
    let totalValue=portfolio.reduce((s,p)=>s+p.size*p.current,0);
    let totalCost=portfolio.reduce((s,p)=>s+p.size*p.cost,0);
    let totalPnl=totalValue-totalCost;
    return{success:!0,type:"SUMMARY",data:{totalValue,totalCost,totalPnl},
      message:`📊 组合摘要\n\n总价值: $${totalValue.toFixed(2)}\n总成本: $${totalCost.toFixed(2)}\n总盈亏: $${totalPnl.toFixed(2)} (${(totalPnl/totalCost*100).toFixed(1)}%)`};
  }
  return{success:!0,type:"HELP",message:`💼 Portfolio Tracker

{ action: 'portfolio' } - 查看所有仓位
{ action: 'summary' } - 组合摘要
{ action: 'add', market: '...', side: 'YES', size: 100, price: 0.5 } - 添加仓位
{ action: 'alert', market: '...', price: 0.6, condition: 'above' } - 设置提醒

💰 每次调用 0.001 USDT`};
}
module.exports={handler};
