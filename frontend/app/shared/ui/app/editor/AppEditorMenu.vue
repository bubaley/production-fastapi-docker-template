<template>
  <div class="editor-menu">
    <AppButton
      v-for="button in buttons"
      :key="button.name"
      :icon="button.icon"
      :severity="button.isActive?.() ? 'primary' : 'secondary'"
      :variant="button.isActive?.() ? 'filled' : 'text'"
      size="small"
      @click="button.action()"
    />
    <AppButton
      v-if="editor.isActive('link')"
      icon="lucide:unlink"
      severity="secondary"
      variant="text"
      size="small"
      @click="unsetLink"
    />
  </div>
</template>

<script setup lang="ts">
import type { Editor } from '@tiptap/vue-3'

const props = defineProps<{
  editor: Editor
}>()

const editorFocus = () => props.editor.chain().focus()

const buttons = [
  {
    name: 'bold',
    icon: 'lucide:bold',
    title: 'Жирный',
    isActive: () => props.editor.isActive('bold'),
    action: () => editorFocus().toggleBold().run(),
  },
  {
    name: 'italic',
    icon: 'lucide:italic',
    title: 'Курсив',
    isActive: () => props.editor.isActive('italic'),
    action: () => editorFocus().toggleItalic().run(),
  },
  {
    name: 'underline',
    icon: 'lucide:underline',
    title: 'Подчеркивание',
    isActive: () => props.editor.isActive('underline'),
    action: () => editorFocus().toggleUnderline().run(),
  },
  {
    name: 'strike',
    icon: 'lucide:strikethrough',
    title: 'Зачеркивание',
    isActive: () => props.editor.isActive('strike'),
    action: () => editorFocus().toggleStrike().run(),
  },
  {
    name: 'code',
    icon: 'lucide:code',
    title: 'Код',
    isActive: () => props.editor.isActive('code'),
    action: () => editorFocus().toggleCode().run(),
  },
  {
    name: 'codeBlock',
    icon: 'lucide:code-2',
    title: 'Блок кода',
    isActive: () => props.editor.isActive('codeBlock'),
    action: () => editorFocus().toggleCodeBlock().run(),
  },
  {
    name: 'link',
    icon: 'lucide:link',
    title: 'Ссылка',
    isActive: () => props.editor.isActive('link'),
    action: () => {
      const url = window.prompt('Введите URL:', props.editor.getAttributes('link').href)
      if (url) {
        editorFocus().extendMarkRange('link').setLink({ href: url }).run()
      }
    },
  },
]

const unsetLink = () => {
  editorFocus().unsetLink().run()
}
</script>

<style lang="scss" scoped>
.editor-menu {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: var(--bg-base, #ffffff);
  border: 1px solid var(--border-base, #e5e7eb);
  border-radius: var(--radius-md, 0.5rem);
  padding: 0.25rem;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.menu-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm, 0.25rem);
  cursor: pointer;
  color: var(--fg-base, #1f2937);
  transition: all 0.15s ease;

  &:hover {
    background: var(--bg-tertiary, rgba(0, 0, 0, 0.05));
  }

  &.active {
    background: var(--p-primary-color, #7e5ef4);
    color: var(--p-primary-contrast-color, white);
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px var(--p-primary-color, #7e5ef4);
  }
}
</style>
