import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Settings, 
  Play, 
  Square, 
  Wifi, 
  WifiOff, 
  CheckCircle, 
  XCircle,
  AlertTriangle,
  Info
} from 'lucide-react'
import { notify } from './Notifications'

const API_BASE_URL = 'https://j6h5i7cp7515.manus.space/api'

export default function BetfairIntegration({ user }) {
  const [config, setConfig] = useState({
    username: '',
    password: '',
    app_key: '',
    cert_files: null
  })
  const [isConfigured, setIsConfigured] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState(null)
  const [markets, setMarkets] = useState([])
  const [selectedMarket, setSelectedMarket] = useState('')
  const [automationStatus, setAutomationStatus] = useState(null)

  useEffect(() => {
    checkAutomationStatus()
    const interval = setInterval(checkAutomationStatus, 5000) // Check every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const checkAutomationStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/betfair/status`)
      if (response.ok) {
        const status = await response.json()
        setAutomationStatus(status)
        setIsRunning(status.is_running)
      }
    } catch (error) {
      console.error('Error checking automation status:', error)
    }
  }

  const handleConfigChange = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const testConnection = async () => {
    if (!config.username || !config.password || !config.app_key) {
      notify.error('Por favor, preencha todos os campos obrigatórios')
      return
    }

    setIsConnecting(true)
    setConnectionStatus(null)

    try {
      const response = await fetch(`${API_BASE_URL}/betfair/test-connection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          betfair_config: config
        })
      })

      const result = await response.json()

      if (result.success) {
        setConnectionStatus({
          success: true,
          message: result.message,
          markets_found: result.markets_found
        })
        setIsConfigured(true)
        notify.success('Conexão com Betfair estabelecida com sucesso!')
        
        // Load available markets
        loadMarkets()
      } else {
        setConnectionStatus({
          success: false,
          message: result.message
        })
        notify.error(`Erro na conexão: ${result.message}`)
      }
    } catch (error) {
      setConnectionStatus({
        success: false,
        message: `Erro de conexão: ${error.message}`
      })
      notify.error(`Erro de conexão: ${error.message}`)
    } finally {
      setIsConnecting(false)
    }
  }

  const loadMarkets = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/betfair/markets`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          betfair_config: config
        })
      })

      if (response.ok) {
        const result = await response.json()
        setMarkets(result.markets || [])
      }
    } catch (error) {
      console.error('Error loading markets:', error)
    }
  }

  const startAutomation = async () => {
    if (!isConfigured) {
      notify.error('Configure e teste a conexão primeiro')
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/betfair/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: user.id,
          betfair_config: config,
          target_market_id: selectedMarket || null
        })
      })

      const result = await response.json()

      if (response.ok) {
        setIsRunning(true)
        notify.success('Automação da Betfair iniciada!')
      } else {
        notify.error(`Erro ao iniciar automação: ${result.error}`)
      }
    } catch (error) {
      notify.error(`Erro ao iniciar automação: ${error.message}`)
    }
  }

  const stopAutomation = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/betfair/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      const result = await response.json()

      if (response.ok) {
        setIsRunning(false)
        notify.success('Automação da Betfair parada!')
      } else {
        notify.error(`Erro ao parar automação: ${result.error}`)
      }
    } catch (error) {
      notify.error(`Erro ao parar automação: ${error.message}`)
    }
  }

  const testManualSpin = async () => {
    const randomNumber = Math.floor(Math.random() * 37) // 0-36
    
    try {
      const response = await fetch(`${API_BASE_URL}/betfair/manual-spin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: user.id,
          winning_number: randomNumber
        })
      })

      const result = await response.json()

      if (response.ok) {
        notify.success(`Spin manual simulado: ${randomNumber}`)
      } else {
        notify.error(`Erro no spin manual: ${result.error}`)
      }
    } catch (error) {
      notify.error(`Erro no spin manual: ${error.message}`)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Integração Betfair</h1>
          <p className="text-gray-600">Configure a conexão com a API da Betfair para apostas automáticas</p>
        </div>
        
        <div className="flex items-center space-x-2">
          {isRunning ? (
            <Badge variant="default" className="bg-green-500">
              <Play className="h-3 w-3 mr-1" />
              Ativo
            </Badge>
          ) : (
            <Badge variant="secondary">
              <Square className="h-3 w-3 mr-1" />
              Parado
            </Badge>
          )}
        </div>
      </div>

      {/* Configuration Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            Configuração da API
          </CardTitle>
          <CardDescription>
            Configure suas credenciais da Betfair API para habilitar a automação
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="username">Usuário Betfair</Label>
              <Input
                id="username"
                type="text"
                value={config.username}
                onChange={(e) => handleConfigChange('username', e.target.value)}
                placeholder="Seu usuário da Betfair"
              />
            </div>
            
            <div>
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                type="password"
                value={config.password}
                onChange={(e) => handleConfigChange('password', e.target.value)}
                placeholder="Sua senha da Betfair"
              />
            </div>
          </div>
          
          <div>
            <Label htmlFor="app_key">Application Key</Label>
            <Input
              id="app_key"
              type="text"
              value={config.app_key}
              onChange={(e) => handleConfigChange('app_key', e.target.value)}
              placeholder="Sua chave de aplicação da Betfair"
            />
          </div>

          <div className="flex space-x-2">
            <Button 
              onClick={testConnection} 
              disabled={isConnecting || isRunning}
              variant="outline"
            >
              {isConnecting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary mr-2"></div>
                  Testando...
                </>
              ) : (
                <>
                  <Wifi className="h-4 w-4 mr-2" />
                  Testar Conexão
                </>
              )}
            </Button>
            
            {isConfigured && (
              <Button onClick={testManualSpin} variant="outline">
                <Info className="h-4 w-4 mr-2" />
                Testar Spin Manual
              </Button>
            )}
          </div>

          {/* Connection Status */}
          {connectionStatus && (
            <Alert className={connectionStatus.success ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
              {connectionStatus.success ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <XCircle className="h-4 w-4 text-red-600" />
              )}
              <AlertDescription className={connectionStatus.success ? 'text-green-800' : 'text-red-800'}>
                {connectionStatus.message}
                {connectionStatus.markets_found !== undefined && (
                  <span className="block mt-1">
                    Mercados de roleta encontrados: {connectionStatus.markets_found}
                  </span>
                )}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Automation Control */}
      {isConfigured && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              {isRunning ? (
                <Play className="h-5 w-5 mr-2 text-green-600" />
              ) : (
                <Square className="h-5 w-5 mr-2 text-gray-600" />
              )}
              Controle da Automação
            </CardTitle>
            <CardDescription>
              Inicie ou pare a automação das apostas na Betfair
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {markets.length > 0 && (
              <div>
                <Label htmlFor="market">Mercado de Roleta (Opcional)</Label>
                <select
                  id="market"
                  value={selectedMarket}
                  onChange={(e) => setSelectedMarket(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="">Selecionar automaticamente</option>
                  {markets.map((market) => (
                    <option key={market.market_id} value={market.market_id}>
                      {market.market_name} - {market.event_name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="flex space-x-2">
              {!isRunning ? (
                <Button onClick={startAutomation} className="bg-green-600 hover:bg-green-700">
                  <Play className="h-4 w-4 mr-2" />
                  Iniciar Automação
                </Button>
              ) : (
                <Button onClick={stopAutomation} variant="destructive">
                  <Square className="h-4 w-4 mr-2" />
                  Parar Automação
                </Button>
              )}
            </div>

            {/* Status Information */}
            {automationStatus && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium mb-2">Status da Automação</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Status:</span>
                    <span className={`ml-2 font-medium ${isRunning ? 'text-green-600' : 'text-gray-600'}`}>
                      {automationStatus.status}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Mercados Ativos:</span>
                    <span className="ml-2 font-medium">{automationStatus.active_markets}</span>
                  </div>
                </div>
                
                {automationStatus.markets && automationStatus.markets.length > 0 && (
                  <div className="mt-2">
                    <span className="text-gray-600 text-sm">Mercados Monitorados:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {automationStatus.markets.map((marketId) => (
                        <Badge key={marketId} variant="outline" className="text-xs">
                          {marketId}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Info className="h-5 w-5 mr-2" />
            Como Configurar
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm text-gray-600">
            <div className="flex items-start">
              <div className="bg-blue-100 text-blue-800 rounded-full w-6 h-6 flex items-center justify-center text-xs font-medium mr-3 mt-0.5">1</div>
              <div>
                <p className="font-medium text-gray-900">Obtenha suas credenciais da Betfair</p>
                <p>Acesse o portal de desenvolvedores da Betfair e obtenha seu Application Key</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className="bg-blue-100 text-blue-800 rounded-full w-6 h-6 flex items-center justify-center text-xs font-medium mr-3 mt-0.5">2</div>
              <div>
                <p className="font-medium text-gray-900">Configure suas credenciais</p>
                <p>Insira seu usuário, senha e Application Key nos campos acima</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className="bg-blue-100 text-blue-800 rounded-full w-6 h-6 flex items-center justify-center text-xs font-medium mr-3 mt-0.5">3</div>
              <div>
                <p className="font-medium text-gray-900">Teste a conexão</p>
                <p>Clique em "Testar Conexão" para verificar se as credenciais estão corretas</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className="bg-blue-100 text-blue-800 rounded-full w-6 h-6 flex items-center justify-center text-xs font-medium mr-3 mt-0.5">4</div>
              <div>
                <p className="font-medium text-gray-900">Configure suas estratégias</p>
                <p>Vá para a página "Estratégias" e ative as estratégias que deseja usar</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className="bg-blue-100 text-blue-800 rounded-full w-6 h-6 flex items-center justify-center text-xs font-medium mr-3 mt-0.5">5</div>
              <div>
                <p className="font-medium text-gray-900">Inicie a automação</p>
                <p>Clique em "Iniciar Automação" para começar as apostas automáticas</p>
              </div>
            </div>
          </div>
          
          <Alert className="mt-4">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>Importante:</strong> Certifique-se de que suas estratégias estão configuradas e ativadas antes de iniciar a automação. 
              A automação irá monitorar os resultados da roleta e executar apostas automaticamente baseadas nas suas estratégias ativas.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  )
}

