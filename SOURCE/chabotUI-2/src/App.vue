<template>
  <v-app id="inspire">
    <v-toolbar color="primary lighten-1" dark fixed app>
      <v-layout row align-center>
          <v-toolbar-title>ADOBOT</v-toolbar-title>
      </v-layout>
    </v-toolbar>
    <v-content>
      <router-view></router-view>
    </v-content>
    <v-footer color="primary lighten-1" app>
      <span class="white--text">&copy; FIT - HCMUS - CHATBOT</span>
    </v-footer>
  </v-app>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style lang="stylus">
  @import './stylus/main'
</style>
