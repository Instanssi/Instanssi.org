import { VuetifyTiptap, VuetifyViewer, createVuetifyProTipTap } from "vuetify-pro-tiptap";
import {
    BaseKit,
    Blockquote,
    Bold,
    BulletList,
    Clear,
    Code,
    CodeBlock,
    Color,
    FontFamily,
    FontSize,
    Fullscreen,
    Heading,
    Highlight,
    History,
    HorizontalRule,
    Indent,
    Italic,
    Link,
    OrderedList,
    Strike,
    SubAndSuperScript,
    Table,
    TaskList,
    TextAlign,
    Underline,
    Video,
} from "vuetify-pro-tiptap";
import "vuetify-pro-tiptap/style.css";

export const vuetifyTipTap = createVuetifyProTipTap({
    lang: "en",
    components: {
        VuetifyTiptap,
        VuetifyViewer,
    },
    extensions: [
        BaseKit,
        Bold,
        Italic,
        Underline,
        Strike,
        Code.configure({ divider: true }),
        Heading,
        TextAlign,
        FontFamily,
        FontSize,
        Color,
        Highlight.configure({ divider: true }),
        SubAndSuperScript.configure({ divider: true }),
        Clear.configure({ divider: true }),
        BulletList,
        OrderedList,
        TaskList,
        Indent.configure({ divider: true }),
        Link,
        Video,
        Table.configure({ divider: true }),
        Blockquote,
        HorizontalRule,
        CodeBlock.configure({ divider: true }),
        History.configure({ divider: true }),
        Fullscreen,
    ],
});