<template>
  <div v-if="editor" class="container">
    <div class="control-group">
      <div class="button-group">
        <div
          v-for="button in formattingButtons"
          :key="button.title"
          :title="button.title"
          :class="['editor-button', { 'is-active': button.isActive() }]"
          @click="button.action"
        >
          <span v-html="button.label"></span>
        </div>

        <div
          v-for="emoji in emojis"
          :key="emoji.char"
          :title="emoji.name"
          class="editor-button"
          @click="insertEmoji(emoji.char)"
        >
          {{ emoji.char }}
        </div>

        <div class="emoji-dropdown" @click.stop>
          <div class="editor-button" @click="toggleEmojiDropdown" title="All emojis">
            all emojis
          </div>
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

    <!-- Link Dialog -->
    <v-dialog v-model="linkDialog" persistent max-width="400px">
      <v-card>
        <v-card-title>Insert or Edit Link</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="linkText"
            label="Text"
            @keydown.enter.prevent="applyLink"
          />
          <v-text-field
            v-model="linkUrl"
            label="URL"
            @keydown.enter.prevent="applyLink"
          />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn text @click="removeLink" v-if="isEditingLink">Remove</v-btn>
          <v-spacer />
          <v-btn text @click="closeLinkDialog">Cancel</v-btn>
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
  components: { EditorContent },
  props: {
    modelValue: {
      type: String,
      default: "",
    },
  },
  data() {
    return {
      editor: null,
      localHtml: "",
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
      linkDialog: false,
      linkText: "",
      linkUrl: "",
      isEditingLink: false,
    }
  },
  computed: {
    filteredAllEmojis() {
      return this.allEmojis.filter((emoji) =>
        emoji.name.toLowerCase().includes(this.emojiSearch.toLowerCase())
      )
    },
    formattingButtons() {
      return [
        {
          label: "<strong>B</strong>",
          title: "Bold",
          isActive: () => this.editor.isActive("bold"),
          action: () => this.editor.chain().focus().toggleBold().run(),
        },
        {
          label: "<em>I</em>",
          title: "Italic",
          isActive: () => this.editor.isActive("italic"),
          action: () => this.editor.chain().focus().toggleItalic().run(),
        },
        {
          label: "<s>S</s>",
          title: "Strikethrough",
          isActive: () => this.editor.isActive("strike"),
          action: () => this.editor.chain().focus().toggleStrike().run(),
        },
        {
          label: "H1",
          title: "Heading 1",
          isActive: () => this.editor.isActive("heading", { level: 1 }),
          action: () => this.editor.chain().focus().toggleHeading({ level: 1 }).run(),
        },
        {
          label: "h2",
          title: "Heading 2",
          isActive: () => this.editor.isActive("heading", { level: 2 }),
          action: () => this.editor.chain().focus().toggleHeading({ level: 2 }).run(),
        },
        {
          label: "• List",
          title: "Bullet List",
          isActive: () => this.editor.isActive("bulletList"),
          action: () => this.editor.chain().focus().toggleBulletList().run(),
        },
        {
          label: "1. List",
          title: "Ordered List",
          isActive: () => this.editor.isActive("orderedList"),
          action: () => this.editor.chain().focus().toggleOrderedList().run(),
        },
        {
          label: "Link",
          title: "Insert link",
          isActive: () => false,
          action: this.setLink,
        },
        {
          label: "Divider",
          title: "Insert divider",
          isActive: () => false,
          action: () => this.editor.chain().focus().setHorizontalRule().run(),
        },
        {
          label: "[ hard break ]",
          title: "Insert hard break",
          isActive: () => false,
          action: () => this.editor.chain().focus().setHardBreak().run(),
        },
      ]
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
        this.localHtml = editor.getHTML()
      },
    })
  },
  beforeUnmount() {
    if (this.editor) this.editor.destroy()
    document.removeEventListener("click", this.handleClickOutside)
  },
  methods: {
    getHtml() {
      return this.editor ? this.editor.getHTML() : ""
    },
    insertEmoji(char) {
      this.editor.chain().focus().insertContent(char + " ").run()
    },
    insertEmojiFromDropdown(char) {
      this.insertEmoji(char)
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
  padding: 1rem;
  font-family: sans-serif;
}

.ProseMirror {
  border: 1px solid #ccc;
  border-radius: 15px;
  min-height: 200px;
  max-height: 400px;
  padding: 10px;
  overflow-y: auto;
}

.button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.editor-button {
  padding: 0.4rem 0.8rem;
  font-size: 0.9rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  background-color: #f9f9f9;
  cursor: pointer;
  user-select: none;

  &.is-active {
    background-color: #dbeafe;
    font-weight: bold;
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
