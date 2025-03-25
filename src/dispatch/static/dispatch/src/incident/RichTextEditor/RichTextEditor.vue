<template>
  <div v-if="editor" class="container">
    <div class="control-group">
      <div class="button-group">
        <button
          @click="editor.chain().focus().toggleBold().run()"
          :disabled="!editor.can().chain().focus().toggleBold().run()"
          :class="{ 'is-active': editor.isActive('bold') }"
        >
          Bold
        </button>
        <button
          @click="editor.chain().focus().toggleItalic().run()"
          :disabled="!editor.can().chain().focus().toggleItalic().run()"
          :class="{ 'is-active': editor.isActive('italic') }"
        >
          Italic
        </button>
        <button
          @click="editor.chain().focus().toggleStrike().run()"
          :disabled="!editor.can().chain().focus().toggleStrike().run()"
          :class="{ 'is-active': editor.isActive('strike') }"
        >
          Strike
        </button>
        <button
          @click="editor.chain().focus().toggleCode().run()"
          :disabled="!editor.can().chain().focus().toggleCode().run()"
          :class="{ 'is-active': editor.isActive('code') }"
        >
          Code
        </button>

        <button @click="editor.chain().focus().unsetAllMarks().run()">Clear marks</button>
        <button @click="editor.chain().focus().clearNodes().run()">Clear nodes</button>

        <button
          @click="editor.chain().focus().setParagraph().run()"
          :class="{ 'is-active': editor.isActive('paragraph') }"
        >
          Paragraph
        </button>

        <button
          v-for="level in 6"
          :key="level"
          @click="editor.chain().focus().toggleHeading({ level }).run()"
          :class="{ 'is-active': editor.isActive('heading', { level }) }"
        >
          H{{ level }}
        </button>

        <button
          @click="editor.chain().focus().toggleBulletList().run()"
          :class="{ 'is-active': editor.isActive('bulletList') }"
        >
          Bullet list
        </button>
        <button
          @click="editor.chain().focus().toggleOrderedList().run()"
          :class="{ 'is-active': editor.isActive('orderedList') }"
        >
          Ordered list
        </button>

        <button
          @click="editor.chain().focus().toggleCodeBlock().run()"
          :class="{ 'is-active': editor.isActive('codeBlock') }"
        >
          Code block
        </button>
        <button
          @click="editor.chain().focus().toggleBlockquote().run()"
          :class="{ 'is-active': editor.isActive('blockquote') }"
        >
          Blockquote
        </button>
        <button @click="editor.chain().focus().setHorizontalRule().run()">Horizontal rule</button>
        <button @click="editor.chain().focus().setHardBreak().run()">Hard break</button>

        <button
          @click="editor.chain().focus().undo().run()"
          :disabled="!editor.can().chain().focus().undo().run()"
        >
          Undo
        </button>
        <button
          @click="editor.chain().focus().redo().run()"
          :disabled="!editor.can().chain().focus().redo().run()"
        >
          Redo
        </button>

        <button
          @click="editor.chain().focus().setColor('#958DF1').run()"
          :class="{ 'is-active': editor.isActive('textStyle', { color: '#958DF1' }) }"
        >
          Purple
        </button>

        <div class="emoji-group">
          <button v-for="emoji in emojis" :key="emoji" @click="insertEmoji(emoji)">
            {{ emoji }}
          </button>
        </div>
      </div>
    </div>

    <editor-content :editor="editor" class="tiptap" />
  </div>
</template>

<script>
import { Color } from "@tiptap/extension-color"
import ListItem from "@tiptap/extension-list-item"
import TextStyle from "@tiptap/extension-text-style"
import StarterKit from "@tiptap/starter-kit"
import { Editor, EditorContent } from "@tiptap/vue-3"

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
      emojis: ["🔴", "🟡", "🟢", "📌", "❗", "●", "➡️", "🖇"],
    }
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
        StarterKit,
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
    insertEmoji(emoji) {
      this.editor
        .chain()
        .focus()
        .insertContent(emoji + " ")
        .run()
    },
  },
}
</script>

<style lang="scss" scoped>
.container {
  padding: 1rem;
  font-family: sans-serif;
}

.tiptap {
  .ProseMirror {
    border: 1px solid black;
    border-radius: 15px;
    min-height: 80%;
    padding: 10px;
    margin: 10px;
  }

  :first-child {
    margin-top: 0;
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
      background: #f0f0f0;
    }
  }
}
</style>
