<template>
  <v-layout row>
    <v-flex xs12 style="position: relative;">
       <div class="chat-container">
        <v-layout v-for="message in messages" :key="message.index">
          <v-flex>
              <div class="text-xs-right" v-if="message.owner === 'user'">
                <v-chip color="#66a3ff" class="white--text">{{message.message}}</v-chip>
              </div>
              <div class="text-xs-left" v-else-if="message.owner === 'botimg'">
                <v-img :src="message.message" max-width="60%"></v-img>
              </div>
              <div class="text-xs-left" v-else-if="message.owner === 'botvideo'">
                <a class="chat" :href="message.message" >{{message.message}}</a>
              </div>
              <div class="text-xs-left" v-else-if="message.owner === 'button'">
                <v-btn small round color="success" dark @click="getStep(message.message)">{{message.message}}</v-btn>
              </div>
              <div class="text-xs-left" v-else>
                 <p class="chat">{{message.message}}</p>
              </div>
          </v-flex>
        </v-layout>
      </div>
      <div class="typer">
        <v-flex class="ma-2">
              <v-text-field
                label="Chat with me ..."
                hide-details
                single-line
                outline
                v-model="userMessage"
                v-on:keyup.enter="userChat()"
              ></v-text-field>
            </v-flex>
      </div>
    </v-flex>
  </v-layout>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      userMessage: null,
      botResponse: [],
      query: null,
      errors: [],
      messages: [
        {
          owner: 'bot',
          message: 'Hi! I am Adobot. Nice to meet you!'
        },
      ]
    }
  },
  methods: {
    async getStep (process) {
      this.userMessage = process
      this.userChat()
    },
    async userChat () {
      if (this.userMessage != null) {
        var message = {
          owner: 'user',
          message: this.userMessage
        }
        this.messages.push(message)
        this.scrollToEnd()
        await this.getBotResponse()
        for (var i = 0; i < this.botResponse.length; i++) {
          this.messages.push(this.botResponse[i])
        }
        this.botResponse = []
        this.scrollToEnd()
        this.userMessage = null
      }
    },
    scrollToEnd () {
      this.$nextTick(() => {
        var container = this.$el.querySelector('.chat-container')
        container.scrollTop = container.scrollHeight
      })
    },
    sleep (milliseconds) {
      var start = new Date().getTime()
      for (var i = 0; i < 1e7; i++) {
        if ((new Date().getTime() - start) > milliseconds) {
          break
        }
      }
    },
    async getBotResponse () {
      await axios.post(`https://services.fit.hcmus.edu.vn:272/chat`, {
        query: this.userMessage,
      })
        .then(response => {
          var text = response.data[0].text.replace(/'/g, '"')
          text = text.replace(/"s /g, ' is ')
          text = text.replace(/"m /g, ' am ')
          text = text.replace(/"re /g, ' are ')
          text = text.replace(/n"t /g, 'n not ')
          text = JSON.parse(text.replace(/"ve /g, ' have'))
          text.forEach(item => {
            if (item.hasOwnProperty('confirm')) {
              var message1 = {
                owner: 'bot',
                message: item.confirm
              }
              this.botResponse.push(message1)
            }
            if (item.hasOwnProperty('respone')) {
              var message1 = {
                owner: 'bot',
                message: item.respone
              }
              this.botResponse.push(message1)
            }
            if (item.hasOwnProperty('video')) {
              var link = {
                owner: 'botvideo',
                message: item.video[1].link,
              }
              var message2 = {
                owner: 'bot',
                message: item.video[0].res_video,
              }
              this.botResponse.push(message2)
              this.botResponse.push(link)
            }
            if (item.hasOwnProperty('image')) {
              var message3 = {
                owner: 'botimg',
                message: item.image
              }
              this.botResponse.push(message3)
            }
            if (item.hasOwnProperty('type')) {
              this.botResponse.push({owner: 'bot', message: 'Sorry, I can not find the correct answer for you. But i have some data seem to be your question. Choose one for detail if it match your question. If not, please ask another question.'})
              item.type.forEach(element => {
                this.botResponse.push({owner: 'button', message: element})
              })
            }
            if (item.hasOwnProperty('step')) {
              item.step.forEach(i => {
                var message4 = {
                  owner: 'bot',
                  message: 'Step ' + i.stt + ': ' + i.content
                }
                this.botResponse.push(message4)
                if (i.hasOwnProperty('TalkImage')) {
                  message4 = {
                    owner: 'botimg',
                    message: i.TalkImage
                  }
                  this.botResponse.push(message4)
                }
              })
            }
            if (item.hasOwnProperty('process')) {
              var process = item.process
              if (process != null) {
                var num = process.length
                this.botResponse.push({owner: 'bot', message: 'I have found ' + num + ' ways to do that. Please click one you want for details: '})
                for (var i = 1; i <= num; i++) {
                  this.botResponse.push({owner: 'button', message: process[i - 1]})
                }
              }
            }
          })
        })
        .catch(e => {
          console.log(e)
          this.errors.push(e)
        })
      return this.botResponse
    }
  }
}
</script>
<style>
.typer{
    box-sizing: border-box;
    display: flex;
    align-items: center;
    bottom: 0;
    height: 4.9rem;
    width: 100%;
    background-color: white;
    box-shadow: 0 -5px 10px -5px rgba(0,0,0,.2);
  }
.chat-container{
    box-sizing: border-box;
    height: calc(100vh - 12rem);
    overflow-y: auto;
    padding: 10px;
    background-color: white;
}
a.chat{
  background-color: lightgrey;
  border-radius: 20px;
  border: 10px solid lightgrey;
  font-size: 13px;
  width: 60%;
}
</style>
