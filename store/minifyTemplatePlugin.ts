// Can't figure out how the Webpack HTML minifier ever worked with Vue templates.
const RE_HTML = /\.html\?minify$/;

export const minifyTemplatePlugin = () => {
  return {
    name: "minify-html",

    async transform(src: string, id: string) {
      if (id.match(RE_HTML)) {
        return {
          // warning: dangerously high quality minifier (works for our short templates)
          code: `export default ${JSON.stringify(src.replace(/\s+/g, " "))}`,
          map: null,
        };
      }
    },
  };
};
