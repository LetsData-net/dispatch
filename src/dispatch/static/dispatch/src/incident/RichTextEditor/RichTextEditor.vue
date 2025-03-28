<template>
  <div v-if="editor" class="container">
    <div class="control-group">
      <div class="button-group">
        <button
          @click="editor.chain().focus().toggleBold().run()"
          :disabled="!editor.can().chain().focus().toggleBold().run()"
          :class="{ 'is-active': editor.isActive('bold') }"
          title="Bold"
        >
          <strong>B</strong>
        </button>

        <button
          @click="editor.chain().focus().toggleItalic().run()"
          :disabled="!editor.can().chain().focus().toggleItalic().run()"
          :class="{ 'is-active': editor.isActive('italic') }"
          title="Italic"
        >
          <em>I</em>
        </button>

        <button
          @click="editor.chain().focus().toggleStrike().run()"
          :disabled="!editor.can().chain().focus().toggleStrike().run()"
          :class="{ 'is-active': editor.isActive('strike') }"
          title="Strikethrough"
        >
          <s>S</s>
        </button>

        <button
          @click="editor.chain().focus().toggleHeading({ level: 1 }).run()"
          :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }"
          title="Heading 1"
        >
          H1
        </button>

        <button
          @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
          :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }"
          title="Heading 2"
        >
          h2
        </button>

        <button
          @click="editor.chain().focus().toggleBulletList().run()"
          :class="{ 'is-active': editor.isActive('bulletList') }"
          title="Bullet list"
        >
          • List
        </button>

        <button
          @click="editor.chain().focus().toggleOrderedList().run()"
          :class="{ 'is-active': editor.isActive('orderedList') }"
          title="Numbered list"
        >
          1. List
        </button>

        <button @click="setLink" title="Insert link">Link</button>

        <button
          @click="editor.chain().focus().setHorizontalRule().run()"
          title="Insert divider"
        >
          Divider
        </button>

        <button
          @click="editor.chain().focus().setHardBreak().run()"
          title="Insert hard break"
        >
          [ hard break ]
        </button>

        <button
          v-for="emoji in emojis"
          :key="emoji.char"
          @click="insertEmoji(emoji.char)"
          :title="emoji.name"
        >
          {{ emoji.char }}
        </button>

        <div class="emoji-dropdown">
          <button @click="showEmojiDropdown = !showEmojiDropdown" title="All emojis">
            all emojis
          </button>
          <div v-if="showEmojiDropdown" class="emoji-dropdown-list">
            <input
              type="text"
              v-model="emojiSearch"
              placeholder="Search emojis..."
              class="emoji-search"
            />
            <div class="emoji-list-wrapper">
              <div class="emoji-list">
                <span
                  v-for="emoji in filteredAllEmojis"
                  :key="emoji.char"
                  @click="insertEmojiFromDropdown(emoji.char)"
                  :title="emoji.name"
                  class="emoji-item"
                >
                  {{ emoji.char }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="editor-wrapper">
      <editor-content :editor="editor" class="tiptap ProseMirror" />
    </div>
  </div>
</template>

<script>
import { Color } from "@tiptap/extension-color"
import ListItem from "@tiptap/extension-list-item"
import TextStyle from "@tiptap/extension-text-style"
import StarterKit from "@tiptap/starter-kit"
import { Editor, EditorContent } from "@tiptap/vue-3"
import Link from "@tiptap/extension-link"
import emojiData from "emoji.json"

export default {
  name: "RichTextEditor",
  components: {
    EditorContent,
  },
  props: {
    modelValue: {
      type: String,
      default: "",
    },
  },
  emits: ["update:modelValue"],
  data() {
    return {
      editor: null,
      emojis: [
        { char: "📌", name: "pushpin" },
        { char: "➡️", name: "right arrow" },
        { char: "🔇", name: "muted speaker" },
        { char: "❗", name: "exclamation mark" },
        { char: "🔴", name: "red circle" },
        { char: "🟡", name: "yellow circle" },
        { char: "🟢", name: "green circle" },
      ],
      allEmojis: emojiData.map(e => ({ char: e.char, name: e.name })),
      showEmojiDropdown: false,
      emojiSearch: "",
    }
  },
  computed: {
    filteredAllEmojis() {
      return this.allEmojis.filter((emoji) => {
        return emoji.name.toLowerCase().includes(this.emojiSearch.toLowerCase())
      })
    },
  },
  watch: {
    modelValue(newValue) {
      if (this.editor && newValue !== this.editor.getHTML()) {
        this.editor.commands.setContent(newValue, false)
      }
    },
  },
  mounted() {
    this.editor = new Editor({
      extensions: [
        Color.configure({ types: [TextStyle.name, ListItem.name] }),
        TextStyle.configure({ types: [ListItem.name] }),
        StarterKit.configure({ codeBlock: false, blockquote: false }),
        Link.configure({
          openOnClick: true,
          autolink: true,
          HTMLAttributes: {
            class: 'tiptap-link',
            target: '_blank',
            rel: 'noopener noreferrer',
          },
        }),
      ],
      content: this.modelValue,
      onUpdate: ({ editor }) => {
        this.$emit("update:modelValue", editor.getHTML())
      },
    })
  },
  beforeUnmount() {
    if (this.editor) {
      this.editor.destroy()
    }
  },
  methods: {
    insertEmoji(emojiChar) {
      this.editor.chain().focus().insertContent(emojiChar + " ").run()
    },
    insertEmojiFromDropdown(emojiChar) {
      this.insertEmoji(emojiChar)
      this.showEmojiDropdown = false
      this.emojiSearch = ""
    },
    setLink() {
      const previousUrl = this.editor.getAttributes("link").href
      const url = window.prompt("Enter the URL", previousUrl)
      if (url === null) return
      if (url === "") {
        this.editor.chain().focus().unsetLink().run()
        return
      }
      this.editor.chain().focus().setLink({ href: url }).run()
    },
  },
}
</script>

<style lang="scss" scoped>
.container {
  padding: 1rem;
  font-family: sans-serif;
}

.ProseMirror {
  border: 1px solid #ccc;
  border-radius: 15px;
  min-height: 400px;
  padding: 10px;
}

.tiptap {
  :first-child {
    margin-top: 0;
    min-height: 400px;
  }

  p {
    padding: 10px;
    margin: 10px;
  }

  ul,
  ol {
    padding: 0 1rem;
    margin: 1.25rem 1rem 1.25rem 0.4rem;

    li p {
      margin-top: 0.25em;
      margin-bottom: 0.25em;
    }
  }

  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    line-height: 1.1;
    margin-top: 2.5rem;
  }

  h1,
  h2 {
    margin-top: 3.5rem;
    margin-bottom: 1.5rem;
  }

  h1 {
    font-size: 1.4rem;
  }

  h2 {
    font-size: 1.2rem;
  }

  h3 {
    font-size: 1.1rem;
  }

  h4,
  h5,
  h6 {
    font-size: 1rem;
  }

  code {
    background-color: var(--purple-light);
    border-radius: 0.4rem;
    color: var(--black);
    font-size: 0.85rem;
    padding: 0.25em 0.3em;
  }

  pre {
    background: var(--black);
    border-radius: 0.5rem;
    color: var(--white);
    font-family: "JetBrainsMono", monospace;
    margin: 1.5rem 0;
    padding: 0.75rem 1rem;

    code {
      background: none;
      color: inherit;
      font-size: 0.8rem;
      padding: 0;
    }
  }

  blockquote {
    border-left: 3px solid var(--gray-3);
    margin: 1.5rem 0;
    padding-left: 1rem;
  }

  hr {
    border: none;
    border-top: 1px solid var(--gray-2);
    margin: 2rem 0;
  }
}

.button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;

  button {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
    border: 1px solid #ccc;
    border-radius: 6px;
    background-color: #f9f9f9;
    cursor: pointer;

    &.is-active {
      background-color: #dbeafe;
      font-weight: bold;
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
}

.emoji-group {
  display: flex;
  gap: 0.4rem;
  margin-top: 0.5rem;

  button {
    font-size: 1.2rem;
    padding: 0.3rem 0.5rem;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    transition: 0.2s;

    &:hover {
      background: #f9f9f9;
    }
  }
}

.emoji-dropdown-list {
  position: absolute;
  top: 110%;
  left: 0;
  background: white;
  border: 1px solid #ccc;
  padding: 0.5rem;
  border-radius: 6px;
  z-index: 10;
  width: 240px;
}

.emoji-search {
  width: 100%;
  margin-bottom: 0.5rem;
  padding: 0.3rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.emoji-list-wrapper {
  max-height: 200px;
  overflow-y: auto;
}

.emoji-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.emoji-item {
  font-size: 1.4rem;
  padding: 0.25rem;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}

.emoji-item:hover {
  background: #f0f0f0;
}
</style>
