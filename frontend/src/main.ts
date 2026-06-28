import { createApp } from 'vue';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import { createPinia } from 'pinia';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import App from './App.vue';
import router from './router';
import './styles.css';

gsap.registerPlugin(ScrollTrigger);

createApp(App)
  .use(createPinia())
  .use(router)
  .use(ElementPlus)
  .mount('#app');
