import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('./views/Dashboard.vue')
  },
  {
    path: '/routers',
    name: 'Routers',
    component: () => import('./views/Routers.vue')
  },
  {
    path: '/routers/:id',
    name: 'RouterDetail',
    component: () => import('./views/RouterDetail.vue'),
    children: [
      {
        path: '',
        name: 'RouterOverview',
        component: () => import('./views/router/Overview.vue')
      },
      {
        path: 'interfaces',
        name: 'RouterInterfaces',
        component: () => import('./views/router/Interfaces.vue')
      },
      {
        path: 'bridges',
        name: 'RouterBridges',
        component: () => import('./views/router/Bridges.vue')
      },
      {
        path: 'dhcp',
        name: 'RouterDHCP',
        component: () => import('./views/router/DHCP.vue')
      },
      {
        path: 'wifi',
        name: 'RouterWiFi',
        component: () => import('./views/router/WiFi.vue')
      },
      {
        path: 'firewall',
        name: 'RouterFirewall',
        component: () => import('./views/router/Firewall.vue')
      },
      {
        path: 'dns',
        name: 'RouterDNS',
        component: () => import('./views/router/DNS.vue')
      },
      {
        path: 'routes',
        name: 'RouterRoutes',
        component: () => import('./views/router/Routes.vue')
      },
      {
        path: 'queues',
        name: 'RouterQueues',
        component: () => import('./views/router/Queues.vue')
      },
      {
        path: 'system',
        name: 'RouterSystem',
        component: () => import('./views/router/System.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
