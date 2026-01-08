import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import Icon from '@/components/ui/icon';

const Index = () => {
  const [activeSection, setActiveSection] = useState('home');

  const stats = [
    { icon: 'Users', label: 'Участников', value: '1,234' },
    { icon: 'Activity', label: 'Онлайн', value: '187' },
    { icon: 'MessageSquare', label: 'Сообщений', value: '45K+' },
    { icon: 'Trophy', label: 'Рейтинг', value: '#1' },
  ];

  const factions = [
    {
      name: 'Полиция',
      description: 'Охрана порядка и защита граждан Russian Town',
      members: 89,
      color: 'bg-blue-600',
    },
    {
      name: 'МЧС',
      description: 'Спасатели и пожарные службы города',
      members: 56,
      color: 'bg-orange-600',
    },
    {
      name: 'Автомеханики',
      description: 'Ремонт и обслуживание техники',
      members: 73,
      color: 'bg-gray-700',
    },
    {
      name: 'Бизнесмены',
      description: 'Торговля и развитие экономики',
      members: 142,
      color: 'bg-green-600',
    },
  ];

  const admins = [
    { name: 'Владимир', role: 'Главный администратор', status: 'online' },
    { name: 'Дмитрий', role: 'Администратор', status: 'online' },
    { name: 'Александра', role: 'Модератор', status: 'offline' },
    { name: 'Михаил', role: 'Модератор', status: 'online' },
  ];

  const news = [
    {
      title: 'Обновление карты города',
      date: '5 января 2026',
      content: 'Добавлены новые районы и улучшена детализация центра города',
    },
    {
      title: 'Новая фракция доступна',
      date: '1 января 2026',
      content: 'Теперь можно вступить в команду Автомехаников',
    },
    {
      title: 'Праздничное событие',
      date: '31 декабря 2025',
      content: 'Новогодние гонки и конкурсы с призами',
    },
  ];

  const rules = [
    'Уважайте других игроков и администрацию',
    'Запрещено использование читов и багов',
    'Следуйте указаниям администрации',
    'РП (Role Play) обязателен в игровых ситуациях',
    'Запрещен мат и оскорбления в чате',
    'Не спамьте в чате и голосовых каналах',
    'Соблюдайте ПДД внутри игрового мира',
    'Не разрушайте постройки других игроков без причины',
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary via-accent to-secondary rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-xl">RT</span>
            </div>
            <div>
              <h1 className="font-heading font-bold text-xl">Russian Town</h1>
              <p className="text-xs text-muted-foreground">Brick Rigs RP Server</p>
            </div>
          </div>
          
          <nav className="hidden md:flex items-center gap-6">
            <button
              onClick={() => setActiveSection('home')}
              className={`text-sm font-medium transition-colors hover:text-primary ${
                activeSection === 'home' ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              Главная
            </button>
            <button
              onClick={() => setActiveSection('about')}
              className={`text-sm font-medium transition-colors hover:text-primary ${
                activeSection === 'about' ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              О сервере
            </button>
            <button
              onClick={() => setActiveSection('rules')}
              className={`text-sm font-medium transition-colors hover:text-primary ${
                activeSection === 'rules' ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              Правила
            </button>
            <button
              onClick={() => setActiveSection('community')}
              className={`text-sm font-medium transition-colors hover:text-primary ${
                activeSection === 'community' ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              Сообщество
            </button>
            <button
              onClick={() => setActiveSection('gallery')}
              className={`text-sm font-medium transition-colors hover:text-primary ${
                activeSection === 'gallery' ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              Галерея
            </button>
          </nav>

          <Button className="bg-[#5865F2] hover:bg-[#4752C4] text-white">
            <Icon name="MessageCircle" className="mr-2 h-4 w-4" />
            Discord
          </Button>
        </div>
      </header>

      {/* Hero Section */}
      {activeSection === 'home' && (
        <section className="relative overflow-hidden russian-pattern">
          <div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent" />
          <div className="container relative py-24 md:py-32">
            <div className="mx-auto max-w-4xl text-center animate-fade-in">
              <Badge className="mb-4 bg-primary/10 text-primary hover:bg-primary/20">
                🎮 Brick Rigs RP Server
              </Badge>
              <h1 className="font-heading text-5xl md:text-7xl font-bold tracking-tight mb-6">
                Добро пожаловать в{' '}
                <span className="text-gradient-russia">Russian Town</span>
              </h1>
              <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
                Лучший русскоязычный Role Play сервер по Brick Rigs. 
                Уникальные фракции, активное комьюнити и незабываемые приключения!
              </p>
              <div className="flex flex-wrap gap-4 justify-center">
                <Button size="lg" className="bg-primary hover:bg-primary/90">
                  <Icon name="Gamepad2" className="mr-2 h-5 w-5" />
                  Начать играть
                </Button>
                <Button size="lg" variant="outline">
                  <Icon name="BookOpen" className="mr-2 h-5 w-5" />
                  Узнать больше
                </Button>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16 max-w-4xl mx-auto">
              {stats.map((stat, index) => (
                <Card key={index} className="text-center hover:shadow-lg transition-shadow">
                  <CardContent className="pt-6">
                    <Icon name={stat.icon as any} className="h-8 w-8 mx-auto mb-3 text-primary" />
                    <div className="text-3xl font-bold font-heading mb-1">{stat.value}</div>
                    <div className="text-sm text-muted-foreground">{stat.label}</div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* News Section */}
            <div className="mt-16 max-w-4xl mx-auto">
              <h2 className="font-heading text-3xl font-bold text-center mb-8">
                📰 Последние новости
              </h2>
              <div className="grid md:grid-cols-3 gap-6">
                {news.map((item, index) => (
                  <Card key={index} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <CardTitle className="text-lg">{item.title}</CardTitle>
                      <CardDescription>{item.date}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">{item.content}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* About Section */}
      {activeSection === 'about' && (
        <section className="container py-16 animate-fade-in">
          <div className="max-w-4xl mx-auto">
            <h2 className="font-heading text-4xl font-bold text-center mb-12">
              О сервере Russian Town
            </h2>
            
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>Что такое Russian Town?</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p>
                  Russian Town - это уникальный русскоязычный Role Play сервер в игре Brick Rigs. 
                  Мы создали целый виртуальный город с развитой инфраструктурой, где каждый может 
                  найти занятие по душе.
                </p>
                <p>
                  На нашем сервере действует система фракций, экономика, правоохранительные органы 
                  и множество других элементов настоящего города. Вы можете стать полицейским, 
                  спасателем, бизнесменом или просто жителем города.
                </p>
              </CardContent>
            </Card>

            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Icon name="Star" className="text-accent" />
                    Особенности
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    <li className="flex items-start gap-2">
                      <Icon name="Check" className="h-5 w-5 text-green-600 mt-0.5" />
                      <span>Активное и дружелюбное комьюнити</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Icon name="Check" className="h-5 w-5 text-green-600 mt-0.5" />
                      <span>Уникальная карта Russian Town</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Icon name="Check" className="h-5 w-5 text-green-600 mt-0.5" />
                      <span>Система фракций и рангов</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Icon name="Check" className="h-5 w-5 text-green-600 mt-0.5" />
                      <span>Регулярные события и конкурсы</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Icon name="Check" className="h-5 w-5 text-green-600 mt-0.5" />
                      <span>Профессиональная администрация</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Icon name="Zap" className="text-accent" />
                    Технические характеристики
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    <li className="flex items-start gap-2">
                      <Icon name="Server" className="h-5 w-5 text-primary mt-0.5" />
                      <span>Стабильный сервер 24/7</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Icon name="Shield" className="h-5 w-5 text-primary mt-0.5" />
                      <span>Защита от читеров</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Icon name="Gauge" className="h-5 w-5 text-primary mt-0.5" />
                      <span>Оптимизированная производительность</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Icon name="Users" className="h-5 w-5 text-primary mt-0.5" />
                      <span>До 32 игроков одновременно</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Icon name="HardDrive" className="h-5 w-5 text-primary mt-0.5" />
                      <span>Собственный Discord сервер</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>
      )}

      {/* Rules Section */}
      {activeSection === 'rules' && (
        <section className="container py-16 animate-fade-in">
          <div className="max-w-4xl mx-auto">
            <h2 className="font-heading text-4xl font-bold text-center mb-4">
              📋 Правила сервера
            </h2>
            <p className="text-center text-muted-foreground mb-12">
              Соблюдение правил обязательно для всех участников сервера
            </p>

            <Card>
              <CardHeader>
                <CardTitle>Основные правила Russian Town</CardTitle>
                <CardDescription>
                  Незнание правил не освобождает от ответственности
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {rules.map((rule, index) => (
                    <div key={index} className="flex items-start gap-4 p-4 rounded-lg bg-muted/50 hover:bg-muted transition-colors">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">
                        {index + 1}
                      </div>
                      <p className="pt-1">{rule}</p>
                    </div>
                  ))}
                </div>

                <Separator className="my-8" />

                <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6">
                  <h3 className="font-heading font-bold text-lg mb-3 flex items-center gap-2">
                    <Icon name="AlertTriangle" className="text-destructive" />
                    Наказания
                  </h3>
                  <ul className="space-y-2 text-sm">
                    <li><strong>Предупреждение</strong> - за мелкие нарушения</li>
                    <li><strong>Мут (1-24 часа)</strong> - за нарушения в чате</li>
                    <li><strong>Кик</strong> - за повторные нарушения</li>
                    <li><strong>Бан (временный)</strong> - за серьезные нарушения</li>
                    <li><strong>Бан (перманентный)</strong> - за читы, грубые нарушения</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>
      )}

      {/* Community Section */}
      {activeSection === 'community' && (
        <section className="container py-16 animate-fade-in">
          <div className="max-w-6xl mx-auto">
            <h2 className="font-heading text-4xl font-bold text-center mb-12">
              👥 Сообщество
            </h2>

            <Tabs defaultValue="factions" className="w-full">
              <TabsList className="grid w-full grid-cols-2 mb-8">
                <TabsTrigger value="factions">Фракции</TabsTrigger>
                <TabsTrigger value="admins">Администрация</TabsTrigger>
              </TabsList>

              <TabsContent value="factions" className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  {factions.map((faction, index) => (
                    <Card key={index} className="hover:shadow-lg transition-shadow">
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <CardTitle className="flex items-center gap-3">
                            <div className={`w-3 h-3 rounded-full ${faction.color}`} />
                            {faction.name}
                          </CardTitle>
                          <Badge variant="secondary">
                            {faction.members} участников
                          </Badge>
                        </div>
                        <CardDescription>{faction.description}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <Button className="w-full" variant="outline">
                          Подать заявку
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="admins" className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  {admins.map((admin, index) => (
                    <Card key={index}>
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white font-bold text-lg">
                              {admin.name[0]}
                            </div>
                            <div>
                              <CardTitle className="text-lg">{admin.name}</CardTitle>
                              <CardDescription>{admin.role}</CardDescription>
                            </div>
                          </div>
                          <div className={`w-3 h-3 rounded-full ${admin.status === 'online' ? 'bg-green-500' : 'bg-gray-400'}`} />
                        </div>
                      </CardHeader>
                    </Card>
                  ))}
                </div>
              </TabsContent>
            </Tabs>

            <Card className="mt-12 bg-[#5865F2] text-white border-0">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Icon name="MessageCircle" className="h-6 w-6" />
                  Присоединяйся к нашему Discord!
                </CardTitle>
                <CardDescription className="text-white/80">
                  Общайся с игроками, следи за новостями и участвуй в событиях
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="secondary" size="lg">
                  Перейти в Discord
                  <Icon name="ArrowRight" className="ml-2 h-5 w-5" />
                </Button>
              </CardContent>
            </Card>
          </div>
        </section>
      )}

      {/* Gallery Section */}
      {activeSection === 'gallery' && (
        <section className="container py-16 animate-fade-in">
          <div className="max-w-6xl mx-auto">
            <h2 className="font-heading text-4xl font-bold text-center mb-4">
              🖼️ Галерея
            </h2>
            <p className="text-center text-muted-foreground mb-12">
              Лучшие моменты из жизни Russian Town
            </p>

            <div className="grid md:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map((item) => (
                <Card key={item} className="overflow-hidden hover:shadow-xl transition-shadow group cursor-pointer">
                  <div className="aspect-video bg-gradient-to-br from-primary/20 via-accent/20 to-secondary/20 flex items-center justify-center group-hover:scale-105 transition-transform">
                    <Icon name="Image" className="h-16 w-16 text-muted-foreground/30" />
                  </div>
                  <CardContent className="pt-4">
                    <p className="text-sm text-muted-foreground">
                      Скриншот #{item} - Russian Town
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="mt-12 text-center">
              <Button size="lg" variant="outline">
                <Icon name="Upload" className="mr-2 h-5 w-5" />
                Загрузить свой скриншот
              </Button>
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="border-t bg-muted/50 mt-16">
        <div className="container py-12">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="font-heading font-bold mb-4">Russian Town</h3>
              <p className="text-sm text-muted-foreground">
                Лучший RP сервер по Brick Rigs
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Навигация</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><button onClick={() => setActiveSection('home')} className="hover:text-primary transition-colors">Главная</button></li>
                <li><button onClick={() => setActiveSection('about')} className="hover:text-primary transition-colors">О сервере</button></li>
                <li><button onClick={() => setActiveSection('rules')} className="hover:text-primary transition-colors">Правила</button></li>
                <li><button onClick={() => setActiveSection('gallery')} className="hover:text-primary transition-colors">Галерея</button></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Сообщество</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-primary transition-colors">Discord</a></li>
                <li><a href="#" className="hover:text-primary transition-colors">VK</a></li>
                <li><a href="#" className="hover:text-primary transition-colors">YouTube</a></li>
                <li><a href="#" className="hover:text-primary transition-colors">Telegram</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Контакты</h4>
              <p className="text-sm text-muted-foreground mb-2">
                Связаться с администрацией:
              </p>
              <Button variant="outline" size="sm" className="w-full">
                <Icon name="Mail" className="mr-2 h-4 w-4" />
                Написать
              </Button>
            </div>
          </div>
          <Separator className="my-8" />
          <div className="text-center text-sm text-muted-foreground">
            <p>© 2026 Russian Town. Brick Rigs RP Server</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
