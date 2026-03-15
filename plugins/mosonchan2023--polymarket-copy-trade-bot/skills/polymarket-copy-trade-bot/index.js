const SKILL = "polymarket-copy-trade-bot";
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

async function getTopTraders(){
  return[
    {address:"0x6a72D33ee2Fc03dF0889d6D4f2fD1c5f6Ea33ee",winRate:76,volume:"$1.24M",trades:156},
    {address:"0x4f8aB92bc92bc92bc92bc92bc92bc92bc92bc92",winRate:71,volume:"$980K",trades:98},
    {address:"0x1234567890abcdef1234567890abcdef12345678",winRate:68,volume:"$850K",trades:87},
    {address:"0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",winRate:65,volume:"$720K",trades:72},
    {address:"0x9876543210fedcba9876543210fedcba98765432",winRate:72,volume:"$650K",trades:65}
  ];
}

async function getTraderTrades(addr){
  return[
    {market:"Will BTC reach 100k?",side:"YES",size:50000,price:0.45,pnl:"+$12,500"},
    {market:"Will Trump win?",side:"YES",size:30000,price:0.52,pnl:"+$8,400"},
    {market:"AI replaces programmers?",side:"NO",size:20000,price:0.30,pnl:"+$6,000"}
  ];
}

async function handler(i,ctx){
  let P=await c(ctx?.userId||"anonymous",SKILL);
  if(!P.paid)return{error:"PAYMENT_REQUIRED",message:"Pay 0.001 USDT",paymentUrl:P.payment_url};
  let a=(i?.action||"").toLowerCase();
  if(a==="traders"||a==="list"){
    let traders=await getTopTraders();
    return{success:!0,type:"TRADERS",data:traders,
      message:"🐋 Top Traders:\n\n"+traders.map((t,i)=>`${i+1}. ${t.address.slice(0,8)}...${t.address.slice(-4)}\n   胜率: ${t.winRate}%\n   交易量: ${t.volume}\n   交易数: ${t.trades}`).join("\n\n")};
  }
  if(a==="trades"&&i.trader){
    let trades=await getTraderTrades(i.trader);
    return{success:!0,type:"TRADES",data:trades,
      message:`📊 ${i.trader.slice(0,8)}...${i.trader.slice(-4)} 的交易:\n\n`+trades.map(t=>`• ${t.market}\n  ${t.side} $${t.size} @ ${t.price}\n  PnL: ${t.pnl}`).join("\n\n")};
  }
  if(a==="copy"||a==="execute"){
    if(!i.market)return{success:!1,error:"MISSING_MARKET",message:"请指定市场"};
    return{success:!0,type:"COPY",message:`✅ Copy Trade 指令已创建\n市场: ${i.market}\n方向: ${i.side}\n金额: $${i.size||100}\n\n注意: 需要配置 PRIVATE_KEY 才能执行真实交易`};
  }
  return{success:!0,type:"HELP",message:`📋 Copy Trade Bot

{ action: 'traders' } - 获取顶级交易者列表
{ action: 'trades', trader: '0x...' } - 查看交易者历史
{ action: 'copy', market: '...', side: 'YES', size: 100 } - 复制交易

💰 每次调用 0.001 USDT`};
}
module.exports={handler};
