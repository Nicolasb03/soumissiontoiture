import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { MapPin, Calculator, Home, Euro, Clock, CheckCircle, MessageCircle, Bot, User } from 'lucide-react'
import './App.css'

function App() {
  const [address, setAddress] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationState, setConversationState] = useState('initial') // 'initial', 'conversation', 'completed'
  const [sessionId, setSessionId] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [progress, setProgress] = useState(0)
  const [totalQuestions, setTotalQuestions] = useState(0)
  const [messages, setMessages] = useState([])
  const [intermediateEstimation, setIntermediateEstimation] = useState(null)
  const [finalEstimation, setFinalEstimation] = useState(null)
  const [clientInfo, setClientInfo] = useState({
    name: '',
    email: '',
    phone: ''
  })
  const [showLeadForm, setShowLeadForm] = useState(false)

  const addMessage = (content, isBot = false, isQuestion = false) => {
    const message = {
      id: Date.now(),
      content,
      isBot,
      isQuestion,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, message])
  }

  const startConversation = async () => {
    if (!address.trim()) return
    
    setIsLoading(true)
    
    try {
      const response = await fetch("https://e5h6i7cn08lj.manus.space/api/conversation/start", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ address: address })
      })
      
      if (!response.ok) {
        throw new Error('Erreur lors du démarrage de la conversation')
      }
      
      const data = await response.json()
      
      setSessionId(data.session_id)
      setCurrentQuestion(data.question)
      setProgress(data.progress)
      setTotalQuestions(data.total_questions)
      setConversationState('conversation')
      
      // Ajouter les messages initiaux
      addMessage(`Parfait ! J'ai trouvé votre propriété à ${address}. Surface estimée de la toiture : ${data.roof_area_sqm} m².`, true)
      addMessage('Je vais vous poser quelques questions pour affiner votre estimation de rénovation.', true)
      addMessage(data.question.question, true, true)
      
    } catch (error) {
      console.error('Erreur:', error)
      alert('Erreur lors du démarrage de la conversation. Veuillez réessayer.')
    } finally {
      setIsLoading(false)
    }
  }

  const answerQuestion = async (answer) => {
    if (!sessionId || !currentQuestion) return
    
    // Ajouter la réponse de l'utilisateur aux messages
    const selectedOption = currentQuestion.options?.find(opt => opt.value === answer)
    addMessage(selectedOption?.label || answer, false)
    
    setIsLoading(true)
    
    try {
      const response = await fetch("https://e5h6i7cn08lj.manus.space/api/conversation/answer", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          session_id: sessionId, 
          answer: answer 
        })
      })
      
      if (!response.ok) {
        throw new Error('Erreur lors de l\'envoi de la réponse')
      }
      
      const data = await response.json()
      
      if (data.completed) {
        // Conversation terminée
        setConversationState('completed')
        setFinalEstimation(data.final_estimation)
        addMessage('Merci pour vos réponses ! Voici votre estimation personnalisée :', true)
      } else {
        // Question suivante
        setCurrentQuestion(data.question)
        setProgress(data.progress)
        
        if (data.intermediate_estimation) {
          setIntermediateEstimation(data.intermediate_estimation)
          addMessage(`Estimation mise à jour : ${data.intermediate_estimation.min.toLocaleString()} € - ${data.intermediate_estimation.max.toLocaleString()} €`, true)
        }
        
        addMessage(data.question.question, true, true)
      }
      
    } catch (error) {
      console.error('Erreur:', error)
      alert('Erreur lors de l\'envoi de la réponse. Veuillez réessayer.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleLeadSubmission = async () => {
    if (!finalEstimation) return
    
    try {
      const leadData = {
        address: finalEstimation.address,
        roof_area_sqm: finalEstimation.roof_area_sqm,
        estimated_cost_min: finalEstimation.estimated_cost_min,
        estimated_cost_max: finalEstimation.estimated_cost_max,
        client_name: clientInfo.name,
        client_email: clientInfo.email,
        client_phone: clientInfo.phone,
        conversation_history: JSON.stringify(finalEstimation.conversation_summary)
      }
      
      const response = await fetch("https://e5h6i7cn08lj.manus.space/api/leads", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(leadData)
      })
      
      if (!response.ok) {
        throw new Error('Erreur lors de l\'enregistrement')
      }
      
      setShowLeadForm(false)
      alert('Merci ! Nous vous contacterons bientôt pour affiner votre devis.')
    } catch (error) {
      console.error('Erreur:', error)
      alert('Erreur lors de l\'enregistrement. Veuillez réessayer.')
    }
  }

  const resetConversation = () => {
    setAddress('')
    setConversationState('initial')
    setSessionId(null)
    setCurrentQuestion(null)
    setProgress(0)
    setTotalQuestions(0)
    setMessages([])
    setIntermediateEstimation(null)
    setFinalEstimation(null)
    setShowLeadForm(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Home className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">ToitureExpert</h1>
                <p className="text-sm text-gray-600">Assistant intelligent pour l'estimation de toiture</p>
              </div>
            </div>
            <Badge variant="secondary" className="bg-green-100 text-green-800">
              <MessageCircle className="h-4 w-4 mr-1" />
              Conversation Personnalisée
            </Badge>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {conversationState === 'initial' && (
          <>
            {/* Hero Section */}
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Obtenez votre devis de toiture personnalisé
              </h2>
              <p className="text-xl text-gray-600 mb-8">
                Notre assistant intelligent vous pose quelques questions pour une estimation précise
              </p>
            </div>

            {/* Address Input Section */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <MapPin className="h-5 w-5 text-blue-600" />
                  <span>Commençons par votre adresse</span>
                </CardTitle>
                <CardDescription>
                  Saisissez l'adresse complète de votre propriété pour démarrer l'estimation personnalisée
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex space-x-4">
                  <Input
                    placeholder="Ex: 123 Rue de la République, 75001 Paris"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    className="flex-1"
                    disabled={isLoading}
                  />
                  <Button 
                    onClick={startConversation}
                    disabled={isLoading || !address.trim()}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {isLoading ? (
                      <>
                        <Clock className="h-4 w-4 mr-2 animate-spin" />
                        Démarrage...
                      </>
                    ) : (
                      <>
                        <MessageCircle className="h-4 w-4 mr-2" />
                        Commencer l'estimation
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {conversationState === 'conversation' && (
          <Card className="mb-8">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center space-x-2">
                  <Bot className="h-5 w-5 text-blue-600" />
                  <span>Conversation avec l'assistant</span>
                </CardTitle>
                <Badge variant="outline">
                  Question {progress} sur {totalQuestions}
                </Badge>
              </div>
              <Progress value={(progress / totalQuestions) * 100} className="w-full" />
            </CardHeader>
            <CardContent>
              {/* Messages */}
              <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.isBot ? 'justify-start' : 'justify-end'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.isBot
                          ? 'bg-blue-100 text-blue-900'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <div className="flex items-start space-x-2">
                        {message.isBot ? (
                          <Bot className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        ) : (
                          <User className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        )}
                        <span className="text-sm">{message.content}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Current Question Options */}
              {currentQuestion && !isLoading && (
                <div className="space-y-3">
                  <h4 className="font-medium text-gray-900">Votre réponse :</h4>
                  <div className="grid gap-2">
                    {currentQuestion.options?.map((option) => (
                      <Button
                        key={option.value}
                        variant="outline"
                        className="justify-start text-left h-auto p-3"
                        onClick={() => answerQuestion(option.value)}
                      >
                        {option.label}
                      </Button>
                    ))}
                  </div>
                </div>
              )}

              {isLoading && (
                <div className="flex items-center justify-center py-4">
                  <Clock className="h-5 w-5 animate-spin mr-2" />
                  <span>Traitement de votre réponse...</span>
                </div>
              )}

              {/* Intermediate Estimation */}
              {intermediateEstimation && (
                <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
                  <h4 className="font-medium text-green-800 mb-2">Estimation en cours</h4>
                  <p className="text-2xl font-bold text-green-900">
                    {intermediateEstimation.min.toLocaleString()} € - {intermediateEstimation.max.toLocaleString()} €
                  </p>
                  <p className="text-sm text-green-700">Cette estimation s'affine avec vos réponses</p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {conversationState === 'completed' && finalEstimation && (
          <>
            {/* Final Estimation */}
            <Card className="mb-8 border-green-200 bg-green-50">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-green-800">
                  <CheckCircle className="h-5 w-5" />
                  <span>Votre estimation personnalisée</span>
                </CardTitle>
                <CardDescription className="text-green-700">
                  Basée sur vos réponses pour {finalEstimation.address}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Price Range */}
                  <div className="bg-white p-6 rounded-lg border">
                    <h3 className="text-lg font-semibold mb-4 flex items-center">
                      <Euro className="h-5 w-5 mr-2 text-green-600" />
                      Fourchette de prix personnalisée
                    </h3>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-gray-900 mb-2">
                        {finalEstimation.estimated_cost_min.toLocaleString()} € - {finalEstimation.estimated_cost_max.toLocaleString()} €
                      </div>
                      <p className="text-sm text-gray-600">
                        Prix basé sur vos spécifications
                      </p>
                    </div>
                  </div>

                  {/* Summary */}
                  <div className="bg-white p-6 rounded-lg border">
                    <h3 className="text-lg font-semibold mb-4">Résumé de vos choix</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span>Surface : {finalEstimation.roof_area_sqm} m²</span>
                      </div>
                      {Object.entries(finalEstimation.conversation_summary).map(([key, value]) => (
                        <div key={key} className="flex items-center space-x-2">
                          <CheckCircle className="h-4 w-4 text-green-600" />
                          <span className="capitalize">{key.replace('_', ' ')} : {Array.isArray(value) ? value.join(', ') : value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <Separator className="my-6" />

                {/* Call to Action */}
                <div className="text-center">
                  <p className="text-gray-700 mb-4">
                    Cette estimation vous convient ? Obtenez un devis détaillé gratuit !
                  </p>
                  <div className="flex justify-center space-x-4">
                    <Button 
                      onClick={() => setShowLeadForm(true)}
                      size="lg"
                      className="bg-orange-600 hover:bg-orange-700"
                    >
                      Obtenir un devis détaillé gratuit
                    </Button>
                    <Button 
                      onClick={resetConversation}
                      variant="outline"
                      size="lg"
                    >
                      Nouvelle estimation
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Lead Form */}
            {showLeadForm && (
              <Card className="border-orange-200 bg-orange-50">
                <CardHeader>
                  <CardTitle className="text-orange-800">Demande de devis personnalisé</CardTitle>
                  <CardDescription className="text-orange-700">
                    Laissez-nous vos coordonnées pour recevoir un devis détaillé et personnalisé
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-4 mb-6">
                    <Input
                      placeholder="Votre nom complet"
                      value={clientInfo.name}
                      onChange={(e) => setClientInfo({...clientInfo, name: e.target.value})}
                    />
                    <Input
                      placeholder="Votre email"
                      type="email"
                      value={clientInfo.email}
                      onChange={(e) => setClientInfo({...clientInfo, email: e.target.value})}
                    />
                    <Input
                      placeholder="Votre téléphone"
                      type="tel"
                      value={clientInfo.phone}
                      onChange={(e) => setClientInfo({...clientInfo, phone: e.target.value})}
                      className="md:col-span-2"
                    />
                  </div>
                  <div className="flex space-x-4">
                    <Button 
                      onClick={handleLeadSubmission}
                      className="bg-orange-600 hover:bg-orange-700"
                      disabled={!clientInfo.name || !clientInfo.email}
                    >
                      Envoyer ma demande
                    </Button>
                    <Button 
                      variant="outline"
                      onClick={() => setShowLeadForm(false)}
                    >
                      Annuler
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {/* Features Section */}
        <div className="grid md:grid-cols-3 gap-6 mt-12">
          <Card>
            <CardContent className="p-6 text-center">
              <div className="bg-blue-100 p-3 rounded-full w-fit mx-auto mb-4">
                <MessageCircle className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-semibold mb-2">Conversation intelligente</h3>
              <p className="text-sm text-gray-600">
                Questions personnalisées selon votre situation
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6 text-center">
              <div className="bg-green-100 p-3 rounded-full w-fit mx-auto mb-4">
                <Calculator className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="font-semibold mb-2">Estimation précise</h3>
              <p className="text-sm text-gray-600">
                Prix affiné selon vos réponses et spécifications
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6 text-center">
              <div className="bg-orange-100 p-3 rounded-full w-fit mx-auto mb-4">
                <CheckCircle className="h-6 w-6 text-orange-600" />
              </div>
              <h3 className="font-semibold mb-2">Devis personnalisé</h3>
              <p className="text-sm text-gray-600">
                Proposition adaptée à vos besoins spécifiques
              </p>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-gray-400">
              © 2025 ToitureExpert - Assistant intelligent alimenté par l'IA
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App

