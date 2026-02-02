function o(e){return{offset:(e.page-1)*e.itemsPerPage,limit:e.itemsPerPage,ordering:r(e),search:e.search}}function r(e){if(e.sortBy.length<=0)return;const t=e.sortBy[0];return t.order==="asc"?`${t.key}`:`-${t.key}`}export{o as g};
//# sourceMappingURL=query_tools-BInV9OzK.js.map
