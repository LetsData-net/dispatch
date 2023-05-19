"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[4120],{4137:(e,t,i)=>{i.d(t,{Zo:()=>l,kt:()=>m});var n=i(7294);function a(e,t,i){return t in e?Object.defineProperty(e,t,{value:i,enumerable:!0,configurable:!0,writable:!0}):e[t]=i,e}function r(e,t){var i=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);t&&(n=n.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),i.push.apply(i,n)}return i}function s(e){for(var t=1;t<arguments.length;t++){var i=null!=arguments[t]?arguments[t]:{};t%2?r(Object(i),!0).forEach((function(t){a(e,t,i[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(i)):r(Object(i)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(i,t))}))}return e}function o(e,t){if(null==e)return{};var i,n,a=function(e,t){if(null==e)return{};var i,n,a={},r=Object.keys(e);for(n=0;n<r.length;n++)i=r[n],t.indexOf(i)>=0||(a[i]=e[i]);return a}(e,t);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);for(n=0;n<r.length;n++)i=r[n],t.indexOf(i)>=0||Object.prototype.propertyIsEnumerable.call(e,i)&&(a[i]=e[i])}return a}var c=n.createContext({}),d=function(e){var t=n.useContext(c),i=t;return e&&(i="function"==typeof e?e(t):s(s({},t),e)),i},l=function(e){var t=d(e.components);return n.createElement(c.Provider,{value:t},e.children)},p="mdxType",u={inlineCode:"code",wrapper:function(e){var t=e.children;return n.createElement(n.Fragment,{},t)}},h=n.forwardRef((function(e,t){var i=e.components,a=e.mdxType,r=e.originalType,c=e.parentName,l=o(e,["components","mdxType","originalType","parentName"]),p=d(i),h=a,m=p["".concat(c,".").concat(h)]||p[h]||u[h]||r;return i?n.createElement(m,s(s({ref:t},l),{},{components:i})):n.createElement(m,s({ref:t},l))}));function m(e,t){var i=arguments,a=t&&t.mdxType;if("string"==typeof e||a){var r=i.length,s=new Array(r);s[0]=h;var o={};for(var c in t)hasOwnProperty.call(t,c)&&(o[c]=t[c]);o.originalType=e,o[p]="string"==typeof e?e:a,s[1]=o;for(var d=2;d<r;d++)s[d]=i[d];return n.createElement.apply(null,s)}return n.createElement.apply(null,i)}h.displayName="MDXCreateElement"},75:(e,t,i)=>{i.r(t),i.d(t,{assets:()=>c,contentTitle:()=>s,default:()=>u,frontMatter:()=>r,metadata:()=>o,toc:()=>d});var n=i(7462),a=(i(7294),i(4137));const r={description:"What to expect as an incident participant."},s="Participant",o={unversionedId:"user-guide/incidents/participant",id:"user-guide/incidents/participant",title:"Participant",description:"What to expect as an incident participant.",source:"@site/docs/user-guide/incidents/participant.mdx",sourceDirName:"user-guide/incidents",slug:"/user-guide/incidents/participant",permalink:"/dispatch/docs/user-guide/incidents/participant",draft:!1,editUrl:"https://github.com/netflix/dispatch/edit/master/docs/docs/user-guide/incidents/participant.mdx",tags:[],version:"current",frontMatter:{description:"What to expect as an incident participant."},sidebar:"userGuideSidebar",previous:{title:"Feedback",permalink:"/dispatch/docs/user-guide/incidents/feedback"},next:{title:"Tasks",permalink:"/dispatch/docs/user-guide/incidents/tasks"}},c={},d=[{value:"Reporting",id:"reporting",level:2},{value:"During",id:"during",level:2},{value:"After",id:"after",level:2},{value:"Notifications",id:"notifications",level:2},{value:"Self-service engagement",id:"self-service-engagement",level:2},{value:"How it works",id:"how-it-works",level:3}],l={toc:d},p="wrapper";function u(e){let{components:t,...r}=e;return(0,a.kt)(p,(0,n.Z)({},l,r,{components:t,mdxType:"MDXLayout"}),(0,a.kt)("h1",{id:"participant"},"Participant"),(0,a.kt)("h2",{id:"reporting"},"Reporting"),(0,a.kt)("p",null,"Dispatch attempts to make reporting incidents as easy as possible. Dispatch provides a dedicated incident report form that users throughout the organization can submit to engage incident-related resources."),(0,a.kt)("p",null,"Located at: ",(0,a.kt)("inlineCode",{parentName:"p"},"https://<your-dispatch-domain>/default/incidents/report")),(0,a.kt)("div",{style:{textAlign:"center"}},(0,a.kt)("p",null,(0,a.kt)("img",{src:i(37).Z,width:"624",height:"768"}))),(0,a.kt)("p",null,"Once submitted, the user is presented with all of the incident resources they need to start managing the incident."),(0,a.kt)("div",{style:{textAlign:"center"}},(0,a.kt)("p",null,(0,a.kt)("img",{src:i(17).Z,width:"651",height:"899"}))),(0,a.kt)("div",{style:{textAlign:"center"}},(0,a.kt)("p",null,(0,a.kt)("img",{src:i(2243).Z,width:"630",height:"614"}))),(0,a.kt)("h2",{id:"during"},"During"),(0,a.kt)("p",null,"After an incident is created, Dispatch will engage new participants automatically. Which participants are engaged is determined by rules defined in the Dispatch Admin UI."),(0,a.kt)("p",null,"Each new participant receives a welcome message ","(","Email + Slack",")"," providing them resources and information to orient them for this given incident."),(0,a.kt)("div",{style:{textAlign:"center"}},(0,a.kt)("p",null,(0,a.kt)("img",{alt:"Incident welcome email",src:i(6623).Z,width:"718",height:"919"}))),(0,a.kt)("div",{style:{textAlign:"center"}},(0,a.kt)("p",null,(0,a.kt)("img",{parentName:"p",src:"https://lh4.googleusercontent.com/EgiaPr7p7X-MsmhU7LCNn9BoM0qgqlj-yFBRsxHYGFY6GWSVmYkqNjDzFB-iTNpZBlaxjpVJ_R8HC5jO9gu12ehtIGfT3-7At7lQms-dppkxiFZTyOA8LUQyubCDqLAU23NYwcoQfrw",alt:"Incident welcome slack (ephemeral)"}))),(0,a.kt)("p",null,"Throughout the incident, Dispatch manages the resources necessary to run your investigation, while also providing reminders and notifications."),(0,a.kt)("h2",{id:"after"},"After"),(0,a.kt)("p",null,"After an incident is marked stable, Dispatch continues to help with incident management creating additional resources such as Post Incident Review ","(","PIRs",")"," documents."),(0,a.kt)("h2",{id:"notifications"},"Notifications"),(0,a.kt)("p",null,"In addition to Dispatch engaging individuals that will be directly responsible for managing the incident, it provides notifications for general awareness throughout the organization."),(0,a.kt)("admonition",{type:"info"},(0,a.kt)("p",{parentName:"admonition"},'The new incident notification message includes a "Join" button; this allows individuals to add themselves to the incident ',"(","and its resources",")"," without involvement from the incident commander.")),(0,a.kt)("h2",{id:"self-service-engagement"},"Self-service engagement"),(0,a.kt)("p",null,'Often participants will want to "self-subscribe" to incidents given a set of parameters. Dispatch allows individuals to be automatically engaged given these parameters.'),(0,a.kt)("p",null,"To set up an individual's engagement, navigate to ",(0,a.kt)("inlineCode",{parentName:"p"},"Contact > Individual")," and either edit an existing individual or create a new one."),(0,a.kt)("p",null,"Next, modify the individual's engagement by selecting or adding terms or phrases that you would like to be engaged when found in an incident attributes, inviting the user when a match is found."),(0,a.kt)("p",null,"For more documentation of incident engagement see ",(0,a.kt)("a",{parentName:"p",href:"/dispatch/docs/administration/settings/contact/"},"here"),"."),(0,a.kt)("h3",{id:"how-it-works"},"How it works"),(0,a.kt)("p",null,'For any given set of parameters (incident type, incident priority, title, description, etc.) Dispatch will attempt to engage any individual that has associated with those parameters. Currently, this is an "OR" association between terms. Meaning that if any term is matched, the individual will be pulled into the incident.'),(0,a.kt)("p",null,"As the incident evolves, new information is uncovered. Dispatch will re-evaluate these associations any time those parameters change, adding additional individuals if necessary."),(0,a.kt)("p",null,'As an example, take an incident that is reported as a "Credential Leak". Dispatch will engage any individual that has associated the terms "Credential", "Leak", and "Credential Leak" (case and punctuation are ignored).'),(0,a.kt)("p",null,'Now, if we find out during the investigation that the incident is really a "System Compromise" and we change the description and title appropriately, Dispatch will then pull in individuals associated with the terms "System", "Compromise", and "System Compromise".'))}u.isMDXComponent=!0},17:(e,t,i)=>{i.d(t,{Z:()=>n});const n=i.p+"assets/images/admin-ui-incident-report-receipt-4b01a1dff449bf1529063b6f21f611be.png"},2243:(e,t,i)=>{i.d(t,{Z:()=>n});const n=i.p+"assets/images/admin-ui-incident-report-resources-5d6a22635edbe57c76dea0ed6f3a3a2a.png"},37:(e,t,i)=>{i.d(t,{Z:()=>n});const n=i.p+"assets/images/admin-ui-incident-report-5a616dadb3752d9be89a24266d1ec043.png"},6623:(e,t,i)=>{i.d(t,{Z:()=>n});const n=i.p+"assets/images/email-incident-welcome-914d3a69b7e84fe8e6cdd346d6bca702.png"}}]);