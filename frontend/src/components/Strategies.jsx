import { 
  Plus, 
  Settings, 
  Play, 
  Pause, 
  Trash2, 
  Target,
  Info,
  Save,
  Clock
} from 'lucide-react'
import ScheduleSettings from './ScheduleSettings'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'

const API_BASE_URL = 'https://j6h5i7cp7515.manus.space/api'

const STRATEGY_TYPES = {
  terminal_8: {
    name: 'Terminal 8 (1→6)',
    description: 'Busca o padrão 1→6 para apostar no terminal 8',
    numbers: [12, 28, 7, 29, 18, 22, 8, 11, 14],
    specialBets: { 30: 2 },
    rules: [
      'Até 2 entradas por gatilho',
      'Se bater → parar e aguardar novo gatilho',
      'Se não bater → parar e aguardar novo 1→6',
      'Ignorar se o 8 sair antes da entrada'
    ]
  },
  '3x3_pattern': {
    name: 'Padrão 3x3',
    description: '3 números consecutivos da lista específica',
    numbers: [0, 3, 4, 12, 15, 19, 21, 26, 28, 32, 35],
    specialBets: { 0: 2 },
    rules: [
      'Até 2 entradas por padrão',
      'Não dobrar apostas',
      '1 ficha em cada número + 2 fichas no 0'
    ]
  },
  '2x7_pattern': {
    name: 'Padrão 2x7',
    description: '3 números consecutivos da lista específica',
    numbers: [2, 4, 7, 12, 17, 18, 19, 21, 22, 25, 28, 29, 34, 35],
    specialBets: {},
    rules: [
      'Até 2 entradas por padrão',
      'Não dobrar apostas',
      '1 ficha em cada número da lista'
    ]
  }
}

export default function Strategies({ user }) {
  const [strategies, setStrategies] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [newStrategy, setNewStrategy] = useState({
    name: '',
    strategy_type: 'terminal_8',
    config: {
      chip_value: 1.0,
      max_entries: 2,
      betting_houses: ['betfair']
    },
    schedule_enabled: false,
    start_time: '',
    end_time: '',
    days_of_week: [],
    timezone: 'America/Sao_Paulo'
  })
  const [editingScheduleStrategy, setEditingScheduleStrategy] = useState(null)
  const [isScheduleDialogOpen, setIsScheduleDialogOpen] = useState(false)

  useEffect(() => {
    fetchStrategies()
  }, [user.id])

  const fetchStrategies = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/strategies?user_id=${user.id}`)
      const data = await response.json()
      setStrategies(data)
    } catch (error) {
      setError('Erro ao carregar estratégias')
    } finally {
      setIsLoading(false)
    }
  }

  const createStrategy = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await fetch(`${API_BASE_URL}/strategies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newStrategy,
          user_id: user.id
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setSuccess('Estratégia criada com sucesso!')
        setNewStrategy({
          name: '',
          strategy_type: 'terminal_8',
          config: {
            chip_value: 1.0,
            max_entries: 2,
            betting_houses: ['betfair']
          }
        })
        fetchStrategies()
      } else {
        setError(data.error || 'Erro ao criar estratégia')
      }
    } catch (error) {
      setError('Erro de conexão')
    } finally {
      setIsLoading(false)
    }
  }

  const toggleStrategy = async (strategyId, currentStatus) => {
    try {
      const response = await fetch(`${API_BASE_URL}/strategies/${strategyId}/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        setStrategies(strategies.map(strategy => 
          strategy.id === strategyId 
            ? { ...strategy, is_active: !currentStatus }
            : strategy
        ))
        setSuccess(`Estratégia ${!currentStatus ? 'ativada' : 'desativada'} com sucesso!`)
      }
    } catch (error) {
      setError('Erro ao alterar status da estratégia')
    }
  }

  const deleteStrategy = async (strategyId) => {
    if (!confirm('Tem certeza que deseja excluir esta estratégia?')) return

    try {
      const response = await fetch(`${API_BASE_URL}/strategies/${strategyId}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        setStrategies(strategies.filter(s => s.id !== strategyId))
        setSuccess('Estratégia excluída com sucesso!')
      }
    } catch (error) {
      setError('Erro ao excluir estratégia')
    }
  }

  const handleScheduleUpdate = (updatedStrategy) => {
    setStrategies(strategies.map(s => s.id === updatedStrategy.id ? updatedStrategy : s))
    setSuccess("Agendamento da estratégia atualizado com sucesso!")
  }

  const DAYS_OF_WEEK = [
    { value: 1, label: 'Segunda', short: 'Seg' },
    { value: 2, label: 'Terça', short: 'Ter' },
    { value: 3, label: 'Quarta', short: 'Qua' },
    { value: 4, label: 'Quinta', short: 'Qui' },
    { value: 5, label: 'Sexta', short: 'Sex' },
    { value: 6, label: 'Sábado', short: 'Sáb' },
    { value: 7, label: 'Domingo', short: 'Dom' }
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Estratégias</h1>
        <p className="text-gray-600">Configure e gerencie suas estratégias de apostas</p>
      </div>

      {/* Alerts */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="active" className="w-full">
        <TabsList>
          <TabsTrigger value="active">Estratégias Ativas</TabsTrigger>
          <TabsTrigger value="create">Criar Nova</TabsTrigger>
          <TabsTrigger value="info">Informações</TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="space-y-4">
          {strategies.length === 0 ? (
            <Card>
              <CardContent className="text-center py-8">
                <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Nenhuma estratégia configurada
                </h3>
                <p className="text-gray-600 mb-4">
                  Crie sua primeira estratégia para começar a apostar automaticamente
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {strategies.map((strategy) => (
                <Card key={strategy.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-lg">{strategy.name}</CardTitle>
                        <CardDescription>
                          {STRATEGY_TYPES[strategy.strategy_type]?.name || strategy.strategy_type}
                        </CardDescription>
                      </div>
                      <Badge variant={strategy.is_active ? "default" : "secondary"}>
                        {strategy.is_active ? "Ativa" : "Inativa"}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="text-sm text-gray-600">
                      <p><strong>Valor da ficha:</strong> R$ {strategy.config?.chip_value || 1.0}</p>
                      <p><strong>Max. entradas:</strong> {strategy.config?.max_entries || 2}</p>
                      <p><strong>Casas de apostas:</strong> {strategy.config?.betting_houses?.join(", ") || "Betfair"}</p>
                    </div>
                    
                    {strategy.schedule_enabled && (
                      <Alert className="mt-4">
                        <Clock className="h-4 w-4" />
                        <AlertDescription>
                          Agendado: {strategy.start_time} - {strategy.end_time} ({strategy.days_of_week.map(d => DAYS_OF_WEEK.find(day => day.value === d)?.short).join(", ")})
                        </AlertDescription>
                      </Alert>
                    )}
                    
                    <div className="flex space-x-2">
                      <Button
                        onClick={() => {
                          setEditingScheduleStrategy(strategy)
                          setIsScheduleDialogOpen(true)
                        }}
                        variant="outline"
                        size="sm"
                        className="flex-1"
                      >
                        <Clock className="h-4 w-4 mr-2" />
                        Agendamento
                      </Button>
                      
                      <Button
                        onClick={() => toggleStrategy(strategy.id, strategy.is_active)}
                        variant={strategy.is_active ? "destructive" : "default"}
                        size="sm"
                        className="flex-1"
                      >
                        {strategy.is_active ? (
                          <>
                            <Pause className="h-4 w-4 mr-2" />
                            Pausar
                          </>
                        ) : (
                          <>
                            <Play className="h-4 w-4 mr-2" />
                            Ativar
                          </>
                        )}
                      </Button>
                      
                      <Button
                        onClick={() => deleteStrategy(strategy.id)}
                        variant="outline"
                        size="sm"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                    {strategy.schedule_enabled && (
                      <Alert className="mt-4">
                        <Clock className="h-4 w-4" />
                        <AlertDescription>
                          Agendado: {strategy.start_time} - {strategy.end_time} ({strategy.days_of_week.map(d => DAYS_OF_WEEK.find(day => day.value === d)?.short).join(", ")})
                        </AlertDescription>
                      </Alert>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="create">
          <Card>
            <CardHeader>
              <CardTitle>Criar Nova Estratégia</CardTitle>
              <CardDescription>
                Configure uma nova estratégia de apostas automáticas
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={createStrategy} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Nome da Estratégia</Label>
                  <Input
                    id="name"
                    type="text"
                    placeholder="Ex: Minha Estratégia Terminal 8"
                    value={newStrategy.name}
                    onChange={(e) => setNewStrategy({ ...newStrategy, name: e.target.value })}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="strategy_type">Tipo de Estratégia</Label>
                  <select
                    id="strategy_type"
                    className="w-full p-2 border border-gray-300 rounded-md"
                    value={newStrategy.strategy_type}
                    onChange={(e) => setNewStrategy({ ...newStrategy, strategy_type: e.target.value })}
                  >
                    {Object.entries(STRATEGY_TYPES).map(([key, type]) => (
                      <option key={key} value={key}>{type.name}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="chip_value">Valor da Ficha (R$)</Label>
                  <Input
                    id="chip_value"
                    type="number"
                    step="0.01"
                    min="0.01"
                    value={newStrategy.config.chip_value}
                    onChange={(e) => setNewStrategy({
                      ...newStrategy,
                      config: { ...newStrategy.config, chip_value: parseFloat(e.target.value) }
                    })}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="max_entries">Máximo de Entradas</Label>
                  <Input
                    id="max_entries"
                    type="number"
                    min="1"
                    max="5"
                    value={newStrategy.config.max_entries}
                    onChange={(e) => setNewStrategy({
                      ...newStrategy,
                      config: { ...newStrategy.config, max_entries: parseInt(e.target.value) }
                    })}
                    required
                  />
                </div>

                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Criando...
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Criar Estratégia
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="info" className="space-y-4">
          {Object.entries(STRATEGY_TYPES).map(([key, type]) => (
            <Card key={key}>
              <CardHeader>
                <CardTitle>{type.name}</CardTitle>
                <CardDescription>{type.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Números de Aposta:</h4>
                  <div className="flex flex-wrap gap-2">
                    {type.numbers.map(num => (
                      <Badge key={num} variant="outline">{num}</Badge>
                    ))}
                  </div>
                  {Object.keys(type.specialBets).length > 0 && (
                    <div className="mt-2">
                      <span className="text-sm text-gray-600">Apostas especiais: </span>
                      {Object.entries(type.specialBets).map(([num, chips]) => (
                        <Badge key={num} className="ml-1">{num} ({chips} fichas)</Badge>
                      ))}
                    </div>
                  )}
                </div>
                
                <div>
                  <h4 className="font-medium mb-2">Regras:</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {type.rules.map((rule, index) => (
                      <li key={index}>• {rule}</li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>

      <Dialog open={isScheduleDialogOpen} onOpenChange={setIsScheduleDialogOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Configurar Agendamento</DialogTitle>
          </DialogHeader>
          {editingScheduleStrategy && (
            <ScheduleSettings 
              strategy={editingScheduleStrategy} 
              onUpdate={handleScheduleUpdate} 
              onClose={() => setIsScheduleDialogOpen(false)}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

const DAYS_OF_WEEK = [
  { value: 1, label: 'Segunda', short: 'Seg' },
  { value: 2, label: 'Terça', short: 'Ter' },
  { value: 3, label: 'Quarta', short: 'Qua' },
  { value: 4, label: 'Quinta', short: 'Qui' },
  { value: 5, label: 'Sexta', short: 'Sex' },
  { value: 6, label: 'Sábado', short: 'Sáb' },
  { value: 7, label: 'Domingo', short: 'Dom' }
]