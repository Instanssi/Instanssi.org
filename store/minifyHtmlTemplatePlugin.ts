// Can't figure out how the Webpack HTML minifier ever worked with Vue templates,
// or what Vite plugin could replace it. One I tried stumbled on Vue syntax.

export const minifyHtmlTemplatePlugin = () => {
  const RE_HTML = /\.html\?minify$/;

  return {
    name: "minify-html-template",

    async transform(src: string, id: string) {
      if (id.match(RE_HTML)) {
        return {
          // hey, this works for our short templates and lack of "pre"
          code: `export default ${JSON.stringify(src.replace(/\s+/g, " "))}`,
          map: null,
        };
      }
    },
  };
};
