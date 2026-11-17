<script setup lang="ts">
import { Check, FileQuestion, TriangleAlert } from '@lucide/vue'
import UiDemo from '../../components/UiDemo.vue'
</script>

<template>
  <UiDemo
    title="Outcome"
    code='tone="success" as="h2"'
    description="The end of a flow: icon in a tinted circle, title, text and full-width actions. h2 by default; the error page uses it as h1."
  >
    <div class="mx-auto flex max-w-sm flex-col gap-8">
      <AppResultState
        :icon="Check"
        tone="success"
        title="Email confirmed"
        description="You can now sign in with your new address."
      >
        <template #actions>
          <AppButton
            fluid
            label="Continue"
          />
        </template>
      </AppResultState>
    </div>
  </UiDemo>
  <UiDemo
    title="Error page"
    code='tone="warning" as="h1"'
    description="A whole-page failure. Open a missing route to see the real error page."
  >
    <div class="mx-auto flex max-w-sm flex-col gap-6">
      <AppResultState
        :icon="TriangleAlert"
        tone="warning"
        as="h3"
        title="Something went wrong"
        description="Could not open the page. Try refreshing it in a minute."
      />
      <AppButton
        variant="outline"
        label="Error page (404)"
        :icon="FileQuestion"
        href="/ui/missing-page"
        fluid
      />
    </div>
  </UiDemo>
</template>
