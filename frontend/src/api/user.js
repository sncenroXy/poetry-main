import request from './index'

export const getProfile = () => request.get('/user/profile')
export const updateProfile = (data) => request.put('/user/profile', data)
export const changePassword = (data) => request.put('/user/password', data)

export const getFavorites = (limit = 50) => request.get('/user/favorites', { params: { limit } })
export const getFavoriteStatus = (poemId) => request.get(`/user/favorites/${poemId}/status`)
export const addFavorite = (poemId) => request.post(`/user/favorites/${poemId}`)
export const removeFavorite = (poemId) => request.delete(`/user/favorites/${poemId}`)

export const recordHistory = (poemId) => request.post(`/user/history/${poemId}`)
export const getHistory = (limit = 20) => request.get('/user/history', { params: { limit } })

export const recordLearningEvent = (data) => request.post('/user/learning/events', data)
export const getLearningSummary = () => request.get('/user/learning/summary')
export const getAdaptiveQuiz = (count = 5) => request.post('/user/learning/adaptive-quiz', null, {
  params: { count },
  timeout: 60000,
})

export const saveCreation = (data) => request.post('/user/creations', data)
export const getCreations = (limit = 30) => request.get('/user/creations', { params: { limit } })
export const getRecommendations = (limit = 6) => request.get('/user/recommendations', { params: { limit } })
export const getPortrait = () => request.get('/user/portrait')

export const getWrongAnswers = (limit = 50) => request.get('/user/wrong-answers', { params: { limit } })
export const addWrongAnswer = (data) => request.post('/user/wrong-answers', data)
export const removeWrongAnswer = (id) => request.delete(`/user/wrong-answers/${id}`)
export const clearWrongAnswers = () => request.delete('/user/wrong-answers')
