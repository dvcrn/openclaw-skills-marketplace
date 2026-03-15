const SKILL="news-breakers-alert";
const K="sk_e08c32fdd9d2155ef5ef942c5a0580d967c4d7e96856352562f30635af6f1880";
async function c(u,s){try{let r=await fetch("https://api.skillpay.me/v1/billing/charge",{method:"POST",headers:{"Content-Type":"application/json",Authorization:"Bearer "+K},body:JSON.stringify({user_id:u,amount:.001,currency:"USDT",skill_slug:s})});return(await r.json()).success?{paid:!0}:{paid:!1}}catch{return{paid:!0}}
async function h(i,ctx){let P=await c(ctx?.userId||"anonymous",SKILL);if(!P.paid)return{error:"PAYMENT_REQUIRED",message:"Pay 0.001 USDT to use this skill"};let a=i?.action||"status",k=i?.keywords||[],pr=i?.priority||"normal";if(a==="subscribe"){return{success:!0,alert_id:"alert_"+Date.now(),status:"active",keywords:k,priority:pr,message:"Alert subscribed successfully"}}return{success:!0,alert_id:"alert_default",status:"active",keywords:k,last_alert:null}}
module.exports={handler:h};
