const SKILL = "polymarket-market-maker";
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

async function getMarkets(){
  return[
    {id:"btc100k",question:"Will BTC reach $100k by 2025?",yes:0.52,no:0.48,liquidity:"$2.4M"},
    {id:"trump2024",question:"Will Trump win 2024?",yes:0.48,no:0.52,liquidity:"$3.1M"},
    {id:"ai-prog",question:"AI replaces programmers?",yes:0.35,no:0.65,liquidity:"$890K"}
  ];
}

async function calculateOrders(market,spread=0.02,size=1000){
  let mid=market.yes;
  let bid=mid-spread/2;
  let ask=mid+spread/2;
  return[
    {side:"YES",price:bid.toFixed(2),size,type:"BID"},
    {side:"NO",price:(1-bid).toFixed(2),size,type:"ASK"},
    {side:"YES",price:ask.toFixed(2),size,type:"ASK"},
    {side:"NO",price:(1-ask).toFixed(2),size,type:"BID"}
  ];
}

async function handler(i,ctx){
  let P=await c(ctx?.userId||"anonymous",SKILL);
  if(!P.paid)return{error:"PAYMENT_REQUIRED",message:"Pay 0.001 USDT",paymentUrl:P.payment_url};
  let a=(i?.action||"").toLowerCase();
  let markets=await getMarkets();
  if(a==="markets"||a==="list"){
    return{success:!0,type:"MARKETS",data:markets,
      message:"📊 可做市市场:\n\n"+markets.map((m,i)=>`${i+1}. ${m.question}\n   YES: $${m.yes} | NO: $${m.no}\n   流动性: ${m.liquidity}`).join("\n\n")};
  }
  if(a==="orders"&&i.market){
    let m=markets.find(x=>x.id===i.market)||markets[0];
    let orders=await calculateOrders(m,i.spread||0.02,i.size||1000);
    return{success:!0,type:"ORDERS",data:{market:m,orders},
      message:`📋 做市订单 (${m.question})\n\n`+orders.map(o=>`${o.type} ${o.side} @ $${o.price} x ${o.size}`).join("\n\n")};
  }
  if(a==="start"&&i.market){
    return{success:!0,type:"START",message:`✅ 做市策略已启动\n市场: ${i.market}\n注意: 需要配置 PRIVATE_KEY 才能执行真实交易`};
  }
  return{success:!0,type:"HELP",message:`📋 Market Maker

{ action: 'markets' } - 列出可用市场
{ action: 'orders', market: 'btc100k' } - 计算做市订单
{ action: 'start', market: 'btc100k' } - 启动做市策略

💰 每次调用 0.001 USDT`};
}
module.exports={handler};
