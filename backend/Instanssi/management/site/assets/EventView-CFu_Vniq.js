import{d as K,r as i,a as j,p as G,q as O,s as Q,g as v,k as m,w as r,b as o,n as F,e as a,v as W,u as X,c as Y,F as Z,x as ee,P as I,h as S,t as M,l as N,y as q,z as L,A as ae}from"./index-BRchJf3y.js";import{c as te,a as B,d as le,e as ne,u as se,b as k,V as re}from"./VForm-V8UYkpqE.js";import{V as oe,_ as ie,d as ue,a as de,g as ce}from"./VDataTableServer-CBdXgYM2.js";import{_ as ve,V as R}from"./LayoutBase.vue_vue_type_script_setup_true_lang-DMvDB-5o.js";import{a as z}from"./VRow-CmSCnZ-N.js";const me=K({__name:"EventDialog",setup(H,{expose:n}){const V=i(),{t:s}=j(),x=G(),u=O(),d=i(0),E=Q(()=>p.value?s("EventDialog.labels.isArchived"):s("EventDialog.labels.isNotArchived")),y=te({name:B().required().min(1).max(64),tag:B().required().min(1).max(8),date:le().required(),archived:ne(),mainUrl:B().required().url().max(200)}),{handleSubmit:w,setTouched:_,resetForm:D,setValues:U}=se({validationSchema:y}),f=k("name"),g=k("tag"),c=k("date"),p=k("archived"),b=k("mainUrl"),C=w(async t=>{var l;let e;d.value!==void 0?e=await T(d.value,t):e=await $(t),e&&((l=V.value)==null||l.setResult(!0))});async function $(t){try{return await x.events.eventsCreate({name:t.name,date:t.date,archived:t.archived,tag:t.tag,mainurl:t.mainUrl}),u.success(s("EventDialog.createSuccess")),!0}catch(e){u.error(s("EventDialog.createFailure")),console.error(e)}return!1}async function T(t,e){try{return await x.events.eventsPartialUpdate(t,{name:e.name,date:e.date,archived:e.archived,tag:e.tag,mainurl:e.mainUrl}),u.success(s("EventDialog.editSuccess")),!0}catch(l){u.error(s("EventDialog.editFailure")),console.error(l)}return!1}async function P(t=void 0){var e;return t!==void 0?(d.value=t.id,U({name:t.name,tag:t.tag,date:t.date,archived:t.archived??!1,mainUrl:t.mainurl??""})):(d.value=void 0,D(),_(!1)),await((e=V.value)==null?void 0:e.modal())??!1}return n({modal:P}),(t,e)=>(v(),m(ie,{title:a(s)("EventDialog.title"),"ok-text":a(s)("General.save"),"ok-icon":"fas fa-floppy-disk",width:1e3,onSubmit:a(C),ref_key:"dialog",ref:V},{default:r(()=>[o(re,null,{default:r(()=>[o(F,{modelValue:a(f).value.value,"onUpdate:modelValue":e[0]||(e[0]=l=>a(f).value.value=l),"error-messages":a(f).errorMessage.value,variant:"outlined",label:a(s)("EventDialog.labels.name")},null,8,["modelValue","error-messages","label"]),o(F,{modelValue:a(g).value.value,"onUpdate:modelValue":e[1]||(e[1]=l=>a(g).value.value=l),"error-messages":a(g).errorMessage.value,variant:"outlined",label:a(s)("EventDialog.labels.tag")},null,8,["modelValue","error-messages","label"]),o(F,{type:"date",modelValue:a(c).value.value,"onUpdate:modelValue":e[2]||(e[2]=l=>a(c).value.value=l),"error-messages":a(c).errorMessage.value,variant:"outlined",label:a(s)("EventDialog.labels.date")},null,8,["modelValue","error-messages","label"]),o(F,{modelValue:a(b).value.value,"onUpdate:modelValue":e[3]||(e[3]=l=>a(b).value.value=l),"error-messages":a(b).errorMessage.value,variant:"outlined",label:a(s)("EventDialog.labels.mainUrl")},null,8,["modelValue","error-messages","label"]),o(oe,{modelValue:a(p).value.value,"onUpdate:modelValue":e[4]||(e[4]=l=>a(p).value.value=l),"error-messages":a(p).errorMessage.value,label:E.value},null,8,["modelValue","error-messages","label"])]),_:1})]),_:1},8,["title","ok-text","onSubmit"]))}}),ye=K({__name:"EventView",setup(H){const{t:n,d:V}=j(),s=i(void 0),x=ee(ae),u=O(),d=W(),E=G(),y=X(),w=i(!1),_=[25,50,100],D=i(_[0]),U=i(0),f=i(1),g=i([]),c=i(0),p=[{title:n("EventView.headers.id"),sortable:!0,key:"id"},{title:n("EventView.headers.name"),sortable:!1,key:"name"},{title:n("EventView.headers.tag"),sortable:!1,key:"tag"},{title:n("EventView.headers.date"),sortable:!0,key:"date"},{title:n("EventView.headers.archived"),sortable:!1,key:"archived"},{title:n("EventView.headers.mainUrl"),sortable:!1,key:"mainurl"},{title:n("EventView.headers.actions"),sortable:!1,key:"actions",align:"end"}];async function b(t){w.value=!0;const{offset:e,limit:l,sortBy:h}=ce(t);try{const{count:A,results:J}=await E.events.eventsList(l,void 0,e,h);g.value=J,U.value=A}catch(A){u.error(n("EventView.loadFailure")),console.error(A)}finally{w.value=!1}}const C=ue(b,250);async function $(t){const e=n("EventView.confirmDelete",t);if(await x.value.confirm(e)){try{await E.events.eventsDestroy(t.id),u.success(n("EventView.deleteSuccess"))}catch(h){u.error(n("EventView.deleteFailure")),console.error(h)}c.value+=1,await d.refreshEvents()}}async function T(t){const e=await E.events.eventsRetrieve(t);await s.value.modal(e)&&(c.value+=1,await d.refreshEvents())}async function P(){await s.value.modal()&&(f.value=1,c.value+=1,await d.refreshEvents())}return(t,e)=>(v(),Y(Z,null,[o(ve,{title:a(n)("EventView.title")},{default:r(()=>[o(R,null,{default:r(()=>[o(z,null,{default:r(()=>[a(y).canAdd(a(I).EVENT)?(v(),m(N,{key:0,"prepend-icon":"fas fa-plus",onClick:P},{default:r(()=>[S(M(a(n)("EventView.newEvent")),1)]),_:1})):q("",!0)]),_:1})]),_:1}),o(R,null,{default:r(()=>[o(z,null,{default:r(()=>[(v(),m(de,{class:"elevation-1 primary","item-value":"id",density:"compact",key:`blog-table-${c.value}`,headers:p,items:g.value,"items-length":U.value,loading:w.value,page:f.value,"items-per-page-options":_,"no-data-text":a(n)("EventView.noEventsFound"),"loading-text":a(n)("EventView.loadingEvents"),"items-per-page":D.value,"onUpdate:itemsPerPage":e[0]||(e[0]=l=>D.value=l),"onUpdate:options":a(C)},{"item.archived":r(({item:l})=>[l.archived?(v(),m(L,{key:0,icon:"fas fa-check",color:"green"})):(v(),m(L,{key:1,icon:"fas fa-xmark",color:"red"}))]),"item.date":r(({item:l})=>[S(M(a(V)(l.date,"long")),1)]),"item.actions":r(({item:l})=>[a(y).canDelete(a(I).EVENT)?(v(),m(N,{key:0,density:"compact",variant:"text",onClick:h=>$(l),"prepend-icon":"fas fa-xmark",color:"red"},{default:r(()=>[S("Delete")]),_:2},1032,["onClick"])):q("",!0),a(y).canChange(a(I).EVENT)?(v(),m(N,{key:1,density:"compact",variant:"text",onClick:h=>T(l.id),"prepend-icon":"fas fa-pen-to-square"},{default:r(()=>[S("Edit")]),_:2},1032,["onClick"])):q("",!0)]),_:1},8,["items","items-length","loading","page","no-data-text","loading-text","items-per-page","onUpdate:options"]))]),_:1})]),_:1})]),_:1},8,["title"]),o(me,{ref_key:"dialog",ref:s},null,512)],64))}});export{ye as default};
//# sourceMappingURL=EventView-CFu_Vniq.js.map
