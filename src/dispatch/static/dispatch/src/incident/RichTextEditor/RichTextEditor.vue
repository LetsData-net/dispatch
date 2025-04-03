<template>
  <div v-if="editor" class="container">
    <div class="control-group">
      <div class="button-group">
        <button
          @click="editor.chain().focus().toggleBold().run()"
          type="button"
          :disabled="!editor.can().chain().focus().toggleBold().run()"
          :class="{ 'is-active': editor.isActive('bold') }"
          title="Bold"
        >
          <strong>B</strong>
        </button>

        <button
          @click="editor.chain().focus().toggleItalic().run()"
          type="button"
          :disabled="!editor.can().chain().focus().toggleItalic().run()"
          :class="{ 'is-active': editor.isActive('italic') }"
          title="Italic"
        >
          <em>I</em>
        </button>

        <button
          @click="editor.chain().focus().toggleStrike().run()"
          type="button"
          :disabled="!editor.can().chain().focus().toggleStrike().run()"
          :class="{ 'is-active': editor.isActive('strike') }"
          title="Strikethrough"
        >
          <s>S</s>
        </button>

        <button
          type="button"
          @click="editor.chain().focus().toggleHeading({ level: 1 }).run()"
          :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }"
          title="Heading 1"
        >
          H1
        </button>

        <button
          type="button"
          @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
          :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }"
          title="Heading 2"
        >
          h2
        </button>

        <button
          type="button"
          @click="editor.chain().focus().toggleBulletList().run()"
          :class="{ 'is-active': editor.isActive('bulletList') }"
          title="Bullet list"
        >
          • List
        </button>

        <button
          type="button"
          @click="editor.chain().focus().toggleOrderedList().run()"
          :class="{ 'is-active': editor.isActive('orderedList') }"
          title="Numbered list"
        >
          1. List
        </button>

        <button @click="setLink" title="Insert link" type="button">Link</button>

        <button
          @click="editor.chain().focus().setHorizontalRule().run()"
          type="button"
          title="Insert divider"
        >
          Divider
        </button>

        <button
          @click="editor.chain().focus().setHardBreak().run()"
          type="button"
          title="Insert hard break"
        >
          [ hard break ]
        </button>

        <button
          v-for="emoji in emojis"
          :key="emoji.char"
          @click="insertEmoji(emoji.char)"
          :title="emoji.name"
          type="button"
        >
          {{ emoji.char }}
        </button>

        <div class="emoji-dropdown" @click.stop>
          <button @click="toggleEmojiDropdown" title="All emojis" type="button">all emojis</button>
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
      <editor-content :editor="editor" class="tiptap ProseMirror editor" />
    </div>

    <v-dialog v-model="linkDialog" persistent max-width="400px">
      <v-card>
        <v-card-title>Insert or Edit Link</v-card-title>
        <v-card-text>
          <v-text-field v-model="linkText" label="Text" @keydown.enter.prevent="applyLink" />
          <v-text-field v-model="linkUrl" label="URL" @keydown.enter.prevent="applyLink" />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="removeLink" v-if="isEditingLink">Remove</v-btn>
          <v-spacer />
          <v-btn variant="text" @click="closeLinkDialog">Cancel</v-btn>
          <v-btn color="primary" @click="applyLink">Apply</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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
      allEmojis: emojiData.map((e) => ({ char: e.char, name: e.name })),
      showEmojiDropdown: false,
      emojiSearch: "",
      // Link Dialog
      linkDialog: false,
      linkText: "",
      linkUrl: "",
      isEditingLink: false,
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
    document.addEventListener("click", this.handleClickOutside)
    this.editor = new Editor({
      extensions: [
        Color.configure({ types: [TextStyle.name, ListItem.name] }),
        TextStyle.configure({ types: [ListItem.name] }),
        StarterKit.configure({ codeBlock: false, blockquote: false }),
        Link.configure({
          openOnClick: true,
          autolink: true,
          HTMLAttributes: {
            class: "tiptap-link",
            target: "_blank",
            rel: "noopener noreferrer",
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
    if (this.editor) this.editor.destroy()
    document.removeEventListener("click", this.handleClickOutside)
  },
  methods: {
    insertEmoji(emojiChar) {
      this.editor
        .chain()
        .focus()
        .insertContent(emojiChar + " ")
        .run()
    },
    insertEmojiFromDropdown(emojiChar) {
      this.insertEmoji(emojiChar)
      this.showEmojiDropdown = false
      this.emojiSearch = ""
    },
    toggleEmojiDropdown() {
      this.showEmojiDropdown = !this.showEmojiDropdown
    },
    handleClickOutside(e) {
      if (!this.$el.contains(e.target)) {
        this.showEmojiDropdown = false
      }
    },
    setLink() {
      const { href } = this.editor.getAttributes("link")
      const selectedText = this.editor.state.doc.textBetween(
        this.editor.state.selection.from,
        this.editor.state.selection.to,
        " "
      )
      this.linkUrl = href || ""
      this.linkText = selectedText || href || ""
      this.isEditingLink = !!href
      this.linkDialog = true
    },
    applyLink() {
      if (this.linkUrl === "") {
        this.editor.chain().focus().unsetLink().run()
      } else {
        this.editor
          .chain()
          .focus()
          .insertContent(`<a href="${this.linkUrl}" target="_blank">${this.linkText}</a>`)
          .run()
      }
      this.closeLinkDialog()
    },
    removeLink() {
      this.editor.chain().focus().unsetLink().run()
      this.closeLinkDialog()
    },
    closeLinkDialog() {
      this.linkDialog = false
      this.linkText = ""
      this.linkUrl = ""
      this.isEditingLink = false
    },
  },
}
</script>

<style lang="scss" scoped>
.container {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  min-height: 0;
  padding: 1rem;
}

.editor-wrapper {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.ProseMirror {
  flex-grow: 1;
  overflow-y: auto;
  border: 1px solid #ccc;
  border-radius: 15px;
  min-height: 200px;
  max-height: 400px;
  height: 100%;
  padding: 10px 20px 20px;
  margin: 5px;
  background-color: white;
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

.emoji-dropdown {
  position: relative;
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
