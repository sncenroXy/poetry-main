import request from './index'

export const getCapabilities = () => request.get('/system/capabilities')
