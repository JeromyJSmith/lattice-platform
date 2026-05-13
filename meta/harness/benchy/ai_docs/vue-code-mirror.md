## vue-codemirror6  ![TypeScript icon, indicating that this package has built-in type declarations](https://static-production.npmjs.com/255a118f56f5346b97e56325a1217a16.svg)

1.3.7 • Public • Published a day ago

- [Readme](?activeTab=readme)
- [Code Beta](?activeTab=code)
- [9 Dependencies](?activeTab=dependencies)
- [8 Dependents](?activeTab=dependents)
- [74 Versions](?activeTab=versions)

# vue-codemirror6

[Permalink: vue-codemirror6](#vue-codemirror6)

[![logo](https://user-images.githubusercontent.com/480173/224358008-6ffad05d-1d97-4c18-8554-7d41b03f88ab.png)](https://user-images.githubusercontent.com/480173/224358008-6ffad05d-1d97-4c18-8554-7d41b03f88ab.png)

[![jsdelivr CDN](https://camo.githubusercontent.com/2b1b896a605a7dfab422f7d2b4c5a8dc9687391090b605c159d15a4d2359d3f1/68747470733a2f2f646174612e6a7364656c6976722e636f6d2f76312f7061636b6167652f6e706d2f7675652d636f64656d6972726f72362f6261646765)](https://www.jsdelivr.com/package/npm/vue-codemirror6)[![NPM Downloads](https://camo.githubusercontent.com/9c3cbecdbe462254798daada7d510392ee9d79bc29958b075738c696a9109830/68747470733a2f2f696d672e736869656c64732e696f2f6e706d2f646d2f7675652d636f64656d6972726f72362e7376673f7374796c653d666c6174)](https://www.npmjs.com/package/vue-codemirror6)[![Open in unpkg](https://camo.githubusercontent.com/8c338084ba3d783298b82cb2c37c837b783af4196470d8248df98998e9da5172/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4f70656e253230696e2d756e706b672d626c7565)](https://uiwjs.github.io/npm-unpkg/#/pkg/vue-codemirror6/file/README.md)[![npm version](https://camo.githubusercontent.com/bd7df344ea145f879b76bcb724b05c4f4e2b9f7d2ecac739b42452b0ea7ed5c6/68747470733a2f2f696d672e736869656c64732e696f2f6e706d2f762f7675652d636f64656d6972726f72362e737667)](https://www.npmjs.com/package/vue-codemirror6)[![Open in Gitpod](https://camo.githubusercontent.com/0b9dc4c0929245b0f40fb2439e752ec0c3065afd9dbf68a4b8f7d9a9af9c1449/68747470733a2f2f736869656c64732e696f2f62616467652f4f70656e253230696e2d476974706f642d677265656e3f6c6f676f3d476974706f64)](https://gitpod.io/#https://github.com/logue/vue-codemirror6)[![Twitter Follow](https://camo.githubusercontent.com/b95f12287ab8e98a53cf0a97f554aab4be7101238aa04826eb75e48592405b68/68747470733a2f2f696d672e736869656c64732e696f2f747769747465722f666f6c6c6f772f6c6f6775653235363f7374796c653d706c6173746963)](https://twitter.com/logue256)

A component for using [CodeMirror6](https://codemirror.net/6/) with Vue. This component works in both Vue2 and Vue3.

- [CHANGELOG](https://github.com/logue/vue-codemirror6/blob/HEAD/CHANGELOG.md)

## Usage

[Permalink: Usage](#usage)

```
yarn add vue-codemirror6 codemirror
```

For Vue 2.7 or below, [@vue/composition-api](https://www.npmjs.com/package/@vue/composition-api) is required separately.

```
yarn add vue-codemirror6 @vue/composition-api
```

This component can handle bidirectional binding by `v-model` like a general Vue component.

## Props

[Permalink: Props](#props)

| Props | Type | Information |
| --- | --- | --- |
| model-value | string \| Text | Text value. (Not `value`) |
| basic | boolean | Use [basicSetup](https://codemirror.net/docs/ref/#codemirror.basicSetup). |
| minimal | boolean | Use [miniSetup](https://codemirror.net/docs/ref/#codemirror.minimalSetup). If a `basic` prop is also specified, that setting will take precedence. |
| dark | boolean | Toggle Darkmode. |
| placeholder | string | Add placeholder text (or HTML DOM) when blank |
| wrap | boolean | Line text wrapping. see [lineWrapping](https://codemirror.net/6/docs/ref/#view.EditorView.lineWrapping). |
| tab | boolean | Enables tab indentation. |
| allow-multiple-selections | boolean | Allow Multiple Selection. See [allowMultipleSelections](https://codemirror.net/docs/ref/#state.EditorState%5EallowMultipleSelections) |
| tab-size | number | Configures the tab size to use in this state. |
| line-separator | string | Set line break (separetor) char. (Default is `\n`.) |
| theme | { \[selector: string\]: StyleSpec } | Specify the theme. For example, if you use [@codemirror/theme-one-dark](https://github.com/codemirror/theme-one-dark), import `oneDark` and put it in this prop. |
| readonly | boolean | Makes the cursor visible or you can drag the text but not edit the value. |
| disabled | boolean | This is the reversed value of the CodeMirror editable. Similar to `readonly`, but setting this value to true disables dragging. |
| lang | LanguageSupport | The language you want to have syntax highlighting. see [https://codemirror.net/6/#languages](https://codemirror.net/6/#languages) |
| phrases | Record<string, string> | Specify here if you want to make the displayed character string multilingual. see [https://codemirror.net/6/examples/translate/](https://codemirror.net/6/examples/translate/) |
| extensions | Extension\[\] | Includes enhancements to extend CodeMirror. |
| linter | LintSource | Set Linter. Enter a linter (eg `esLint([arbitrary rule])` function for `@codemirror/lang-javascript`, `jsonParseLinter()` function for `@codemirror/json`). See the sources for various language libraries for more information. |
| linterConfig | Object | see [https://codemirror.net/docs/ref/#lint.linter^config](https://codemirror.net/docs/ref/#lint.linter%5Econfig) |
| forceLinting | boolean | see [https://codemirror.net/docs/ref/#lint.forceLinting](https://codemirror.net/docs/ref/#lint.forceLinting) |
| gutter | boolean | Display 🔴 on the line where there was an error when `linter` was specified. It will not work if `linter` is not specified. |
| gutterConfig | Object | see [https://codemirror.net/docs/ref/#lint.lintGutter^config](https://codemirror.net/docs/ref/#lint.lintGutter%5Econfig) |
| tag | string | HTML tags used in the component. (Default is `div` tag.) |

⚠ Notice: `lang` and `linter` can also be set together in `extensions`. These are separated for compatibility with previous versions of CodeMirror settings and for typing props.

### Supported Languages

[Permalink: Supported Languages](#supported-languages)

#### Official

[Permalink: Official](#official)

- [`@codemirror/lang-angular`](https://www.npmjs.com/package/@codemirror/lang-angular)
- [`@codemirror/lang-cpp`](https://www.npmjs.com/package/@codemirror/lang-cpp)
- [`@codemirror/lang-css`](https://www.npmjs.com/package/@codemirror/lang-css)
- [`@codemirror/lang-html`](https://www.npmjs.com/package/@codemirror/lang-html)
- [`@codemirror/lang-java`](https://www.npmjs.com/package/@codemirror/lang-java)
- [`@codemirror/lang-javascript`](https://www.npmjs.com/package/@codemirror/lang-javascript)
- [`@codemirror/lang-json`](https://www.npmjs.com/package/@codemirror/lang-json)
- [`@codemirror/lang-lezer`](https://www.npmjs.com/package/@codemirror/lang-lezer)
- [`@codemirror/lang-markdown`](https://www.npmjs.com/package/@codemirror/lang-markdown)
- [`@codemirror/lang-php`](https://www.npmjs.com/package/@codemirror/lang-php)
- [`@codemirror/lang-python`](https://www.npmjs.com/package/@codemirror/lang-python)
- [`@codemirror/lang-rust`](https://www.npmjs.com/package/@codemirror/lang-rust)
- [`@codemirror/lang-sql`](https://www.npmjs.com/package/@codemirror/lang-sql)
- [`@codemirror/lang-vue`](https://www.npmjs.com/package/@codemirror/lang-vue)
- [`@codemirror/lang-west`](https://www.npmjs.com/package/@codemirror/lang-west)
- [`@codemirror/lang-xml`](https://www.npmjs.com/package/@codemirror/lang-xml)

### Unofficial

[Permalink: Unofficial](#unofficial)

- [@phoenix-plugin-registry/petetnt.brackets-codemirror-fortran](https://www.npmjs.com/package/@phoenix-plugin-registry/petetnt.brackets-codemirror-fortran)
- [@phoenix-plugin-registry/petetnt.brackets-codemirror-go](https://www.npmjs.com/package/@phoenix-plugin-registry/petetnt.brackets-codemirror-go)
- [`@acarl005/lang-sql`](https://www.npmjs.com/package/@acarl005/lang-sql)
- [`@ark-us/codemirror-lang-taylor`](https://www.npmjs.com/package/@ark-us/codemirror-lang-taylor)
- [`@formulavize/lang-fiz`](https://www.npmjs.com/package/@formulavize/lang-fiz)
- [`@gravitywiz/codemirror-lang-gfcalc`](https://www.npmjs.com/package/@gravitywiz/codemirror-lang-gfcalc)
- [`@nextjournal/lang-clojure`](https://www.npmjs.com/package/@nextjournal/lang-clojure)
- [`@plutojl/lang-julia`](https://www.npmjs.com/package/@plutojl/lang-julia)
- [`@polybase/codemirror-lang-javascript`](https://www.npmjs.com/package/@polybase/codemirror-lang-javascript) - [`@replit/codemirror-lang-nix`](https://www.npmjs.com/package/@replit/codemirror-lang-nix)
- [`@replit/codemirror-lang-csharp`](https://www.npmjs.com/package/@replit/codemirror-lang-csharp)
- [`@replit/codemirror-lang-solidity`](https://www.npmjs.com/package/@replit/codemirror-lang-solidity)
- [`@replit/codemirror-lang-svelte`](https://www.npmjs.com/package/@replit/codemirror-lang-svelte)
- [`@zhijiu/lang-sql`](https://www.npmjs.com/package/@zhijiu/lang-sql)
- [`codemirror-lang-bool`](https://www.npmjs.com/package/codemirror-lang-bool)
- [`codemirror-lang-brainfuck`](https://www.npmjs.com/package/codemirror-lang-brainfuck)
- [`codemirror-lang-cherry`](https://www.npmjs.com/package/codemirror-lang-cherry)
- [`codemirror-lang-chordpro`](https://www.npmjs.com/package/codemirror-lang-chordpro)
- [`codemirror-lang-circom`](https://www.npmjs.com/package/codemirror-lang-circom)
- [`codemirror-lang-edn`](https://www.npmjs.com/package/codemirror-lang-edn)
- [`codemirror-lang-ejs`](https://www.npmjs.com/package/codemirror-lang-ejs)
- [`codemirror-lang-fsl`](https://www.npmjs.com/package/codemirror-lang-fsl)
- [`codemirror-lang-gml`](https://www.npmjs.com/package/codemirror-lang-gml)
- [`codemirror-lang-golfscript`](https://www.npmjs.com/package/codemirror-lang-golfscript)
- [`codemirror-lang-homescript`](https://www.npmjs.com/package/codemirror-lang-homescript)
- [`codemirror-lang-html-n8n`](https://www.npmjs.com/package/codemirror-lang-html-n8n)
- [`codemirror-lang-inform7`](https://www.npmjs.com/package/codemirror-lang-inform7)
- [`codemirror-lang-j`](https://www.npmjs.com/package/codemirror-lang-j)
- [`codemirror-lang-janet`](https://www.npmjs.com/package/codemirror-lang-janet)
- [`codemirror-lang-k`](https://www.npmjs.com/package/codemirror-lang-k)
- [`codemirror-lang-karol`](https://www.npmjs.com/package/codemirror-lang-karol)
- [`codemirror-lang-mermaid`](https://www.npmjs.com/package/codemirror-lang-mermaid)
- [`codemirror-lang-n8n-expression`](https://www.npmjs.com/package/codemirror-lang-n8n-expression)
- [`codemirror-lang-prolog`](https://www.npmjs.com/package/codemirror-lang-prolog)
- [`codemirror-lang-qpen`](https://www.npmjs.com/package/codemirror-lang-qpen)
- [`codemirror-lang-qtam`](https://www.npmjs.com/package/codemirror-lang-qtam)
- [`codemirror-lang-r`](https://www.npmjs.com/package/codemirror-lang-r)
- [`codemirror-lang-rome-ast`](https://www.npmjs.com/package/codemirror-lang-rome-ast)
- [`codemirror-lang-rome`](https://www.npmjs.com/package/codemirror-lang-rome)
- [`codemirror-lang-rush`](https://www.npmjs.com/package/codemirror-lang-rush)
- [`codemirror-lang-scopescript`](https://www.npmjs.com/package/codemirror-lang-scopescript)
- [`codemirror-lang-statement`](https://www.npmjs.com/package/codemirror-lang-statement)
- [`gcode-lang-codemirror`](https://www.npmjs.com/package/gcode-lang-codemirror)
- [`gmail-lang`](https://www.npmjs.com/package/gmail-lang)
- [`lang-bqn`](https://www.npmjs.com/package/lang-bqn)
- [`lang-clojure`](https://www.npmjs.com/package/lang-clojure)
- [`lang-d`](https://www.npmjs.com/package/lang-d)
- [`lang-feel`](https://www.npmjs.com/package/lang-feel)
- [`lang-firestore`](https://www.npmjs.com/package/lang-firestore)

### Supported Themes

[Permalink: Supported Themes](#supported-themes)

- [`@codemirror/theme-one-dark`](https://github.com/codemirror/theme-one-dark)
- [`upleveled/theme-vs-code-dark-plus`](https://github.com/upleveled/theme-vs-code-dark-plus)
- [`codemirror6-bootstrap-theme`](https://github.com/logue/codemirror6-bootstrap-theme)

## Example

[Permalink: Example](#example)

Mark up as follows to make it work at a minimum.

```
<template>
  <code-mirror v-model="value" />
</template>

<script>
import { ref, defineComponent } from 'vue';

import CodeMirror from 'vue-codemirror6';

export default defineComponent({
  components: {
    CodeMirror,
  },
  setup() {
    const value = ref('Cozy lummox gives smart squid who asks for job pen.');

    return { value };
  },
});
</script>
```

### Example using Slots

[Permalink: Example using Slots](#example-using-slots)

The contents of the slot will overwrite the existing `v-model`. For this reason, it is recommended to use it when simply displaying with a `readonly` prop without using `v-model`.

Also, insert a `<pre>` tag to prevent the text in the slot from being automatically formatted.

```
<template>
  <code-mirror :lang="lang" :linter="linter">
    <pre>
{
  "key": "value"
}</pre
    >
  </code-mirror>
</template>

<script>
import { ref, defineComponent } from 'vue';

import { json, jsonParseLinter } from '@codemirror/lang-json';

import CodeMirror from 'vue-codemirror6';

export default defineComponent({
  components: {
    CodeMirror,
  },
  setup() {
    const lang = json();
    const linter = jsonParseLinter();
    return { lang, linter };
  },
});
</script>
```

### Full Example

[Permalink: Full Example](#full-example)

When using as a Markdown editor on [https://github.com/logue/vite-vue3-ts-starter](https://github.com/logue/vue-codemirror6/blob/HEAD/vite-vue3-ts-starter).

```
<script lang="ts" setup>
import { ref, defineComponent, type Ref } from 'vue';

// Load component
import CodeMirror from 'vue-codemirror6';

// CodeMirror extensions
import { markdown as md } from '@codemirror/lang-markdown';
import type { LanguageSupport } from '@codemirror/language';
import type { Extension } from '@codemirror/state';
import type { ViewUpdate } from '@codemirror/view';

/** text */
const value: Ref<string> = ref('');

/** Dark mode **/
const dark: Ref<boolean> = ref(
  window.matchMedia('(prefers-color-scheme: dark)').matches
);

/**
 * CodeMirror Language
 *
 * @see {@link https://codemirror.net/6/docs/ref/#language | @codemirror/language}
 */
const lang: LanguageSupport = md();

/**
 * Internationalization Config.
 * In this example, the display language to Japanese.
 * Must be reactive when used in combination with vue-i18n.
 *
 * @see {@link https://codemirror.net/6/examples/translate/ | Example: Internationalization}
 */
const phrases: Record<string, string> = {
  // @codemirror/view
  'Control character': '制御文字',
  // @codemirror/commands
  'Selection deleted': '選択を削除',
  // @codemirror/language
  'Folded lines': '折り畳まれた行',
  'Unfolded lines': '折り畳める行',
  to: '行き先',
  'folded code': '折り畳まれたコード',
  unfold: '折り畳みを解除',
  'Fold line': '行を折り畳む',
  'Unfold line': '行の折り畳む解除',
  // @codemirror/search
  'Go to line': '行き先の行',
  go: 'OK',
  Find: '検索',
  Replace: '置き換え',
  next: '▼',
  previous: '▲',
  all: 'すべて',
  'match case': '一致条件',
  'by word': '全文検索',
  regexp: '正規表現',
  replace: '置き換え',
  'replace all': 'すべてを置き換え',
  close: '閉じる',
  'current match': '現在の一致',
  'replaced $ matches': '$ 件の一致を置き換え',
  'replaced match on line $': '$ 行の一致を置き換え',
  'on line': 'した行',
  // @codemirror/autocomplete
  Completions: '自動補完',
  // @codemirror/lint
  Diagnostics: 'エラー',
  'No diagnostics': 'エラーなし',
};
</script>

<template>
  <code-mirror
    v-model="value"
    basic
    :dark="dark"
    :lang="lang"
    :phrases="phrases"
  />
</template>
```

## Events

[Permalink: Events](#events)

| Event | Description |
| --- | --- |
| ready | When CodeMirror loaded. |
| focus | When focus changed. |
| update | When CodeMirror state changed. Returns [ViewUpdate](https://codemirror.net/docs/ref/#view.ViewUpdate) object. |
| change | Value changed. Returns [EditorState](https://codemirror.net/docs/ref/#state.EditorState) |

## Parameter / Function

[Permalink: Parameter / Function](#parameter--function)

```
<script setup lang="ts">
import { ref, onMounted, type Ref, type PropType } from 'vue';
import CodeMirror from 'vue-codemirror6';

const cm: Ref<InstanceType<typeof CodeMirror> | undefined> = ref();

onMounted(() => {
  console.log(cm.value?.json);
});
</script>
<template>
  <code-mirror ref="cm" />
</template>
```

| Function / Parameter | Description |
| --- | --- |
| view | Get and set [EditorView](https://codemirror.net/docs/ref/#view.EditorView). |
| selection | Get and set the [EditorSelection](https://codemirror.net/docs/ref/#state.EditorSelection) instance. |
| cursor | Get and set the [cursor](https://codemirror.net/docs/ref/#state.EditorSelection%5Ecursor) location. |
| json | Get and set state to a JSON-serializable object. |
| focus | Get and set [focus](https://codemirror.net/docs/ref/#view.EditorView.focus). |
| lint() | Force run linter (Only if `linter` prop is specified) |
| forceReconfigure() | Re register all extensions. |

### CodeMirror5 backward compatible functions

[Permalink: CodeMirror5 backward compatible functions](#codemirror5-backward-compatible-functions)

The instructions below are compatible methods for those familiar with [codemirror5](https://codemirror.net/5/).
Since the above method is usually sufficient, its **active use is not recommended**.

| Function | Description |
| --- | --- |
| getRange(from?: number, to?: number) | Get the text between the given points in the editor. |
| getLine(number: number) | Get the content of line. |
| lineCount() | Get the number of lines in the editor. |
| getCursor() | Retrieve one end of the primary selection. |
| listSelections() | Retrieves a list of all current selections. |
| getSelection() | Get the currently selected code. |
| getSelections() | The length of the given array should be the same as the number of active selections. |
| somethingSelected() | Return true if any text is selected. |
| replaceRange(replacement: string \| Text, from: number, to: number) | Replace the part of the document between from and to with the given string. |
| replaceSelection(replacement: string \| Text) | Replace the selection(s) with the given string. |
| setCursor(position: number) | Set the cursor position. |
| setSelection(anchor: number, head?: number) | Set a single selection range. |
| setSelections(ranges: readonly SelectionRange\[\], primary?: number) | Sets a new set of selections. |
| extendSelectionsBy(f: Function) | Applies the given function to all existing selections, and calls extendSelections on the result. |

## Recommendations

[Permalink: Recommendations](#recommendations)

Since CodeMirror has a relatively large capacity, when using [vite](https://vitejs.dev), it is recommended to set it to output as a separate file using the [`manualChunks`](https://vitejs.dev/guide/build.html#chunking-strategy) option at build time as shown below.

```
const config: UserConfig = {
  // ...
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // ...
          codemirror: [\
            // Split CodeMirror code.\
            'vue-codemirror6',\
            'codemirror',\
            '@codemirror/autocomplete',\
            '@codemirror/commands',\
            '@codemirror/language',\
            '@codemirror/lint',\
            '@codemirror/search',\
            '@codemirror/state',\
            '@codemirror/view',\
          ],
          'codemirror-lang': [\
            // Add the following as needed.\
            '@codemirror/lang-html',\
            '@codemirror/lang-javascript',\
            '@codemirror/lang-markdown',\
          ],
          // ...
        },
      },
    },
  },
  // ...
};
```

## LICENSE

[Permalink: LICENSE](#license)

©2022-2024 by Logue.
Licensed under the [MIT License](https://github.com/logue/vue-codemirror6/blob/HEAD/LICENSE).

## Readme

### Keywords

- [vuejs](/search?q=keywords:vuejs)
- [vue](/search?q=keywords:vue)
- [vue-components](/search?q=keywords:vue-components)
- [vue-codemirror](/search?q=keywords:vue-codemirror)
- [code-editor](/search?q=keywords:code-editor)
- [text-editor](/search?q=keywords:text-editor)
- [vue2](/search?q=keywords:vue2)
- [vue3](/search?q=keywords:vue3)
- [web-editor](/search?q=keywords:web-editor)
- [vue-plugin](/search?q=keywords:vue-plugin)
- [vue-component](/search?q=keywords:vue-component)
- [codemirror-editor](/search?q=keywords:codemirror-editor)
- [vue-resource](/search?q=keywords:vue-resource)
- [codemirror6](/search?q=keywords:codemirror6)

## Package Sidebar

### Install

`npm i vue-codemirror6`

### Repository

[Gitgithub.com/logue/vue-codemirror6](https://github.com/logue/vue-codemirror6)

### Homepage

[github.com/logue/vue-codemirror6](https://github.com/logue/vue-codemirror6)

### DownloadsWeekly Downloads

1,244

### Version

1.3.7

### License

MIT

### Unpacked Size

110 kB

### Total Files

18

### Issues

[29](https://github.com/logue/vue-codemirror6/issues)

### Pull Requests

[0](https://github.com/logue/vue-codemirror6/pulls)

### Last publish

a day ago

### Collaborators

- [![logue](/npm-avatar/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdmF0YXJVUkwiOiJodHRwczovL3MuZ3JhdmF0YXIuY29tL2F2YXRhci81NWNkNDBmZGRhYTAwNmE3NDNjYmY3NTMyZjAyMWVlMT9zaXplPTEwMCZkZWZhdWx0PXJldHJvIn0.DbwOXF1ocUhyWCKSXyN9tAjlmlN_ZjRMltXnkSzm2lc)](/~logue)


[**Try** on RunKit](https://runkit.com/npm/vue-codemirror6)

[**Report** malware](/support?inquire=security&security-inquire=malware&package=vue-codemirror6&version=1.3.7)
