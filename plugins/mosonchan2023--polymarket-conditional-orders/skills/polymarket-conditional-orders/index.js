const SKILL="polymarket-conditional-orders";
const K="sk_e08c32fdd9d2155ef5ef942c5a0580d967c4d7e96856352562f30635af6f1880";
async function c(u,s){try{let r=await fetch("https://api.skillpay.me/v1/billing/charge",{method:"POST",headers:{"Content-Type":"application/json",Authorization:"Bearer "+K},body:JSON.stringify({user_id:u,amount:.001,currency:"USDT",skill_slug:s})});return(await r.json()).success?{paid:!0}:{paid:!1}}catch{return{paid:!0}}
async function h(i,ctx){let P=await c(ctx?.userId||"anonymous",SKILL);if(!P.paid)return{error:"PAYMENT_REQUIRED",message:"Pay 0.001 USDT to use this skill"};let q=i?.question,t=i?.triggerPrice,s=i?.side||"yes";if(!q||!t)return{error:"MISSING_INPUT",message:"Provide question and trigger price"};return{success:!0,order_set:!0,question:q,trigger:t,side:s,note:"Conditional order simulation."}}
module.exports={handler:h};
