<template>
  <div>
    <router-link
      v-if="!pendingPrerequisites.length"
      :to="link"
      class="link-card"
    >
      <slot></slot>
    </router-link>
    
    <div
      v-if="pendingPrerequisites.length"
      class="link-card prereqs-not-done"
      @click="showModal()"
    >
      <slot></slot>
      <div class="lock">
        <KIcon icon="unlistedchannel" />
      </div>
    </div>

    <KModal
      v-if="modalOpen"
      :title="$tr('prerequisitesText')"
      :submitText="$tr('close')"
      @submit="close"
    >
      <section>
        <ul>
          <li
            v-for="prerequisite in pendingPrerequisites"
            :key="prerequisite.id"
            class="list-link"
          >
            <KRouterLink
              :text="prerequisite.title"
              :to="genLink(prerequisite.id)"
              dir="auto"
              @click.native="close()"
            />
            {{ '(' + Math.round(prerequisite.progress * 100) + '%)' }}
          </li>
        </ul>
      </section>
    </KModal>
  </div>
</template>
  
  
<script>
    import { validateLinkObject } from 'kolibri.utils.validators';
    import { PageNames } from '../constants';
    
    export default {
        name: 'ToggleRouterLink',
        props: {
            link: {
                type: Object,
                required: true,
                validator: validateLinkObject,
            },
            pendingPrerequisites: {
                type: Array,
                required: false,
                default: () => [],
            },
        },
        data() {
            return {
                modalOpen: false,
            }
        },
        methods: {
            showModal() {
                this.modalOpen = true
            },
            close() {
                this.modalOpen = false
            },
            genLink(id) {
                return {
                    name: PageNames.TOPICS_CONTENT,
                    params: { id },
                };
            },
        },
        $trs: {
            prerequisitesText: {
                message: 'Hi, It looks like you need to complete these actvities first',
                context: '',
            },
            close: {
                message: 'Go back',
                context: '',
            },
        },
    };
</script>


<style lang="scss" scoped>
.link-card {
    text-decoration: none;
    &.prereqs-not-done {
        position: relative;
        opacity: 0.3;
    }
    & .lock {
        position: absolute;
        right: 4px;
        bottom: 4px;
    }
}
.list-link {
    font-weight: bold;
    line-height: 32px;
}
</style>