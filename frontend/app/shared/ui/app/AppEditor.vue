<template>
  <div class="telegram-editor">
    <BubbleMenu
      v-if="editor"
      :editor="editor"
      :tippy-options="{ duration: 100 }"
      class="bubble-menu"
    >
      <CEditorMenu :editor="editor" />
    </BubbleMenu>
    <EditorContent
      :editor="editor"
      placeholder="Введите сообщение..."
      class="editor-content"
      :class="editorClass"
    />
  </div>
</template>

<script setup lang="ts">
import { Editor, EditorContent, Extension } from '@tiptap/vue-3'
import { BubbleMenu } from '@tiptap/vue-3/menus'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Link from '@tiptap/extension-link'
import { Placeholder } from '@tiptap/extensions'
import { onBeforeUnmount, watch, onMounted } from 'vue'
import CEditorMenu from './editor/CEditorMenu.vue'

const props = withDefaults(
  defineProps<{
    modelValue?: string | null
    placeholder?: string
    onSend?: () => void
    editorClass?: string
    onFilePaste?: (files: FileList) => void
  }>(),
  {},
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const editor = new Editor({
  extensions: [
    StarterKit.configure({
      heading: false,
      blockquote: false,
      horizontalRule: false,
      bulletList: false,
      orderedList: false,
    }),
    Underline,
    Link.configure({
      openOnClick: false,
      HTMLAttributes: {
        class: 'text-accent underline',
      },
    }),
    Placeholder.configure({
      placeholder: props.placeholder,
    }),
    Extension.create({
      addKeyboardShortcuts() {
        return {
          'Mod-Enter': () => {
            if (props.onSend) {
              props.onSend()
              return true
            }
            return false
          },
        }
      },
    }),
  ],
  content: props.modelValue || '',
  onUpdate: () => {
    emit('update:modelValue', editor.getHTML())
  },
})

watch(
  () => props.modelValue,
  (value) => {
    const isSame = editor.getHTML() === value
    if (isSame) return
    editor.commands.setContent(value || '', { emitUpdate: false })
  },
)

const handlePaste = (event: ClipboardEvent) => {
  if (!props.onFilePaste) return

  const items = event.clipboardData?.items
  if (!items) return

  const files: File[] = []
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (item && item.kind === 'file') {
      const file = item.getAsFile()
      if (file) files.push(file)
    }
  }

  if (files.length > 0) {
    event.preventDefault()
    const fileList = new DataTransfer()
    files.forEach((file) => fileList.items.add(file))
    props.onFilePaste(fileList.files)
  }
}

onMounted(() => {
  const editorElement = editor.view.dom
  editorElement.addEventListener('paste', handlePaste)
})

onBeforeUnmount(() => {
  const editorElement = editor.view.dom
  editorElement.removeEventListener('paste', handlePaste)
  editor.destroy()
})

defineExpose({
  editor,
  focus: () => editor.commands.focus(),
  clear: () => editor.commands.clearContent(),
})
</script>

<style lang="scss" scoped>
.telegram-editor {
  width: 100%;
}

.editor-content {
  :deep(.ProseMirror) {
    outline: none;
    min-height: 2.5rem;
    padding: 0.5rem 0.75rem;
    word-break: break-word;
    overflow-wrap: break-word;
    caret-color: currentColor;

    &:focus {
      outline: none;
    }

    p.is-editor-empty:first-child::before {
      content: attr(data-placeholder);
      float: left;
      color: var(--fg-tertiary, #6b7280);
      pointer-events: none;
      height: 0;
    }

    p {
      margin: 0;
      line-height: 1.5;
    }

    strong,
    b {
      font-weight: 700;
    }

    em,
    i {
      font-style: italic;
    }

    u {
      text-decoration: underline;
    }

    s,
    del {
      text-decoration: line-through;
    }

    code {
      background-color: var(--bg-tertiary, rgba(0, 0, 0, 0.1));
      border-radius: var(--radius-sm, 0.25rem);
      padding: 0.125rem 0.25rem;
      font-family: monospace;
      font-size: 0.9em;
    }

    pre {
      background-color: var(--bg-tertiary, rgba(0, 0, 0, 0.1));
      border-radius: var(--radius-sm, 0.25rem);
      padding: 0.5rem;
      margin: 0.5rem 0;
      overflow-x: auto;

      code {
        background: none;
        padding: 0;
      }
    }

    a {
      color: var(--p-primary-color, #7e5ef4);
      text-decoration: underline;
      cursor: pointer;
    }
  }
}

.bubble-menu {
  :deep(.tippy-box) {
    background: transparent;
    border: none;
    box-shadow: none;
  }
}
</style>
