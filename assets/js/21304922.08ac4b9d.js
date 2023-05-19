"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[1695],{4137:(t,e,n)=>{n.d(e,{Zo:()=>p,kt:()=>m});var i=n(7294);function r(t,e,n){return e in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function o(t,e){var n=Object.keys(t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(t);e&&(i=i.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}))),n.push.apply(n,i)}return n}function a(t){for(var e=1;e<arguments.length;e++){var n=null!=arguments[e]?arguments[e]:{};e%2?o(Object(n),!0).forEach((function(e){r(t,e,n[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(n)):o(Object(n)).forEach((function(e){Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(n,e))}))}return t}function s(t,e){if(null==t)return{};var n,i,r=function(t,e){if(null==t)return{};var n,i,r={},o=Object.keys(t);for(i=0;i<o.length;i++)n=o[i],e.indexOf(n)>=0||(r[n]=t[n]);return r}(t,e);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(t);for(i=0;i<o.length;i++)n=o[i],e.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(t,n)&&(r[n]=t[n])}return r}var c=i.createContext({}),l=function(t){var e=i.useContext(c),n=e;return t&&(n="function"==typeof t?t(e):a(a({},e),t)),n},p=function(t){var e=l(t.components);return i.createElement(c.Provider,{value:e},t.children)},d="mdxType",u={inlineCode:"code",wrapper:function(t){var e=t.children;return i.createElement(i.Fragment,{},e)}},f=i.forwardRef((function(t,e){var n=t.components,r=t.mdxType,o=t.originalType,c=t.parentName,p=s(t,["components","mdxType","originalType","parentName"]),d=l(n),f=r,m=d["".concat(c,".").concat(f)]||d[f]||u[f]||o;return n?i.createElement(m,a(a({ref:e},p),{},{components:n})):i.createElement(m,a({ref:e},p))}));function m(t,e){var n=arguments,r=e&&e.mdxType;if("string"==typeof t||r){var o=n.length,a=new Array(o);a[0]=f;var s={};for(var c in e)hasOwnProperty.call(e,c)&&(s[c]=e[c]);s.originalType=t,s[d]="string"==typeof t?t:r,a[1]=s;for(var l=2;l<o;l++)a[l]=n[l];return i.createElement.apply(null,a)}return i.createElement.apply(null,n)}f.displayName="MDXCreateElement"},9022:(t,e,n)=>{n.r(e),n.d(e,{assets:()=>c,contentTitle:()=>a,default:()=>u,frontMatter:()=>o,metadata:()=>s,toc:()=>l});var i=n(7462),r=(n(7294),n(4137));const o={},a="Notification",s={unversionedId:"administration/settings/incident/notification",id:"administration/settings/incident/notification",title:"Notification",description:"Notifications allow you to specify who should be sent incident notifications (in addition to those directly involved).",source:"@site/docs/administration/settings/incident/notification.mdx",sourceDirName:"administration/settings/incident",slug:"/administration/settings/incident/notification",permalink:"/dispatch/docs/administration/settings/incident/notification",draft:!1,editUrl:"https://github.com/netflix/dispatch/edit/master/docs/docs/administration/settings/incident/notification.mdx",tags:[],version:"current",frontMatter:{},sidebar:"adminSidebar",previous:{title:"Incident Types",permalink:"/dispatch/docs/administration/settings/incident/incident-type"},next:{title:"Workflows",permalink:"/dispatch/docs/administration/settings/incident/workflow"}},c={},l=[],p={toc:l},d="wrapper";function u(t){let{components:e,...o}=t;return(0,r.kt)(d,(0,i.Z)({},p,o,{components:e,mdxType:"MDXLayout"}),(0,r.kt)("h1",{id:"notification"},"Notification"),(0,r.kt)("p",null,"Notifications allow you to specify who should be sent incident notifications (in addition to those directly involved)."),(0,r.kt)("div",{style:{textAlign:"center"}},(0,r.kt)("p",null,(0,r.kt)("img",{src:n(9188).Z,width:"493",height:"797"}))),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Name:")," The name you wish to present to the user."),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Description:")," The description presented to the user when the notification is viewed."),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Type:")," The plugin type that should be used to send the notification (email or conversation)."),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Target:")," The recipient of the notification whatever makes sense for the selected plugin type. (e.g. a Slack conversation name without ",(0,r.kt)("inlineCode",{parentName:"p"},"#")," or an email address.)"),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Filters:")," The search filter which will be used to determine when a notification should be sent."),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Enabled:")," Whether the notification is enabled or not."))}u.isMDXComponent=!0},9188:(t,e,n)=>{n.d(e,{Z:()=>i});const i=n.p+"assets/images/admin-ui-notifications-d270dbe4cf6168304fbd4946a23c494e.png"}}]);