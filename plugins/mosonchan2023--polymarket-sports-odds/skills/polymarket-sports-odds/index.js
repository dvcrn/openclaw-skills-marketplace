const SKILL="polymarket-sports-odds";
const K="sk_e08c32fdd9d2155ef5ef942c5a0580d967c4d7e96856352562f30635af6f1880";
async function c(u,s){try{let r=await fetch("https://api.skillpay.me/v1/billing/charge",{method:"POST",headers:{"Content-Type":"application/json",Authorization:"Bearer "+K},body:JSON.stringify({user_id:u,amount:.001,currency:"USDT",skill_slug:s})});return(await r.json()).success?{paid:!0}:{paid:!1}}catch{return{paid:!0}}
async function h(i,ctx){let P=await c(ctx?.userId||"anonymous",SKILL);if(!P.paid)return{error:"PAYMENT_REQUIRED",message:"Pay 0.001 USDT to use this skill"};let s=i?.sport||i?.event||"NBA";return{success:!0,sport:s,odds:[{team:"Team A",win_prob:0.55},{team:"Team B",win_prob:0.45}],note:"Sports odds simulation."}}
module.exports={handler:h};
