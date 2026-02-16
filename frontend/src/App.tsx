import React, { useEffect } from 'react';
import { useResponsive } from './hooks/useResponsive';
import { Header } from './components/layout/Header';
import { BottomNav } from './components/layout/BottomNav';
import { MessageBubble } from './components/chat/MessageBubble';
import { RouteCard } from './components/chat/RouteCard';
import { InputArea } from './components/chat/InputArea';
import { RouteComparisonView } from './components/chat/RouteComparisonView';
import { Map } from './components/map/Map';
import { LoadingState } from './components/shared/LoadingState';
import { RouteCardSkeleton } from './components/shared/Skeleton';
import { useStore } from './hooks/useStore';
import { MessageSquare, Map as MapIcon, Shield } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
<<<<<<< Updated upstream
=======
import { sendDispatchMessage, fetchRoutes } from './services/api';
>>>>>>> Stashed changes

const App: React.FC = () => {
  const { isMobile, isDesktop } = useResponsive();
  const {
    messages, addMessage, isTyping, setIsTyping,
<<<<<<< Updated upstream
    routes, selectedRouteId, setSelectedRouteId,
    isDarkMode, toggleDarkMode,
    incidents,
    emergencyPhones: phones
=======
    routes, selectedRouteId, setSelectedRouteId, setRoutes,
    isDarkMode, toggleDarkMode,
    incidents,
    emergencyPhones: phones,
    setIncidents,
    setEmergencyPhones,
    userLocation
>>>>>>> Stashed changes
  } = useStore();

  const [activeTab, setActiveTab] = React.useState<'home' | 'chat' | 'map' | 'history' | 'profile'>('chat');
  const [mobileView, setMobileView] = React.useState<'chat' | 'map'>('chat');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

<<<<<<< Updated upstream
  const handleSendMessage = (text: string) => {
=======
  const handleSendMessage = async (text: string) => {
    // Add user message
>>>>>>> Stashed changes
    addMessage({
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date()
    });

<<<<<<< Updated upstream
    // Simulate AI response
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I've analyzed the paths to your destination. Based on current nighttime conditions, I've found ${routes.length} possible routes.`,
        timestamp: new Date()
      });
    }, 3000);
=======
    // Show loading state
    setIsTyping(true);

    try {
      const origin = userLocation ?? { latitude: 38.9446, longitude: -92.3266 };

      const [dispatchResult, routesResult] = await Promise.allSettled([
        sendDispatchMessage(text),
        fetchRoutes({
          origin,
          destination: text,
          user_mode: 'student',
          priority: 'safety',
          time: 'current',
          concerns: []
        })
      ]);

      if (routesResult.status === 'fulfilled') {
        const payload = routesResult.value;
        const rankedRoutes = payload.recommendation.routes;

        setRoutes(rankedRoutes);
        setSelectedRouteId(rankedRoutes.length ? rankedRoutes[0].route.id : null);
        setIncidents(payload.incidents);
        setEmergencyPhones(
          payload.emergency_phones.map((phone, index) => ({
            id: `phone-${index + 1}`,
            location: phone,
            name: 'Emergency Phone'
          }))
        );
      }

      setIsTyping(false);

      if (dispatchResult.status === 'fulfilled') {
        addMessage({
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: dispatchResult.value.response,
          timestamp: new Date()
        });
      } else if (routesResult.status === 'fulfilled') {
        addMessage({
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: routesResult.value.recommendation.explanation,
          timestamp: new Date()
        });
      } else {
        const error = dispatchResult.status === 'rejected' ? dispatchResult.reason : routesResult.reason;
        addMessage({
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
          timestamp: new Date()
        });
      }
    } catch (error) {
      setIsTyping(false);

      addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
        timestamp: new Date()
      });

      console.error('Dispatch API error:', error);
    }
>>>>>>> Stashed changes
  };

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: 'var(--color-bg-primary)',
      color: 'var(--color-text-primary)',
      overflow: 'hidden'
    }}>
      <a href="#main-content" className="skip-link">Skip to main content</a>
      <Header isDarkMode={isDarkMode} toggleDarkMode={toggleDarkMode} />

      <main id="main-content" style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
        {isDesktop ? (
          <div style={{ display: 'flex', height: '100%' }}>
            {/* Desktop Left Sidebar: Chat */}
            <aside style={{
              width: 'var(--chat-width)',
              backgroundColor: 'rgba(255, 255, 255, 0.75)',
              backdropFilter: 'var(--glass-blur)',
              WebkitBackdropFilter: 'var(--glass-blur)',
              borderRight: '1px solid var(--glass-border)',
              display: 'flex',
              flexDirection: 'column',
              zIndex: 10,
              boxShadow: 'var(--glass-shadow)'
            }}>
              <div style={{ flex: 1, overflowY: 'auto', paddingBottom: '20px' }} className="chat-container">
                {messages.map(m => <MessageBubble key={m.id} message={m} />)}

                {isTyping && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
                    <LoadingState />
                    <div style={{ padding: '0 var(--spacing-md)' }}>
                      <RouteCardSkeleton />
                      <RouteCardSkeleton />
                    </div>
                  </div>
                )}

                {!isTyping && messages.length > 1 && (
                  <motion.div
                    initial="hidden"
                    animate="visible"
                    variants={{
                      hidden: { opacity: 0 },
                      visible: {
                        opacity: 1,
                        transition: {
                          staggerChildren: 0.15,
                          delayChildren: 0.4
                        }
                      }
                    }}
                  >
                    <motion.div
                      variants={{ hidden: { opacity: 0, x: -10 }, visible: { opacity: 1, x: 0 } }}
                      style={{ padding: '0 var(--spacing-md)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}
                    >
                      <Shield size={16} color="var(--color-brand-blue)" />
                      <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-brand-blue)' }}>SAFETY RECOMMENDATIONS</span>
                    </motion.div>

                    {routes.map((r) => (
                      <motion.div
                        key={r.route.id}
                        variants={{
                          hidden: { opacity: 0, y: 20, scale: 0.95 },
                          visible: { opacity: 1, y: 0, scale: 1 }
                        }}
                        transition={{ type: 'spring', stiffness: 50, damping: 15 }}
                      >
                        <RouteCard
                          rankedRoute={r}
                          isSelected={selectedRouteId === r.route.id}
                          onSelect={setSelectedRouteId}
                        />
                      </motion.div>
                    ))}

                    {routes.length >= 2 && (
                      <motion.div
                        variants={{ hidden: { opacity: 0 }, visible: { opacity: 1 } }}
                        transition={{ delay: 0.8 }}
                      >
                        <RouteComparisonView recommended={routes[0]} alternative={routes[1]} />
                      </motion.div>
                    )}

                    {routes.length > 0 && (
                      <div role="status" aria-live="polite" className="sr-only">
                        Found {routes.length} safe routes to your destination.
                      </div>
                    )}
                  </motion.div>
                )}
              </div>
              <InputArea onSendMessage={handleSendMessage} />
            </aside>

            {/* Desktop Right: Map */}
            <section style={{ flex: 1, position: 'relative' }}>
              <Map
                routes={routes}
                selectedRouteId={selectedRouteId}
                setSelectedRouteId={setSelectedRouteId}
                incidents={incidents}
                phones={phones}
              />
            </section>
          </div>
        ) : (
          /* Mobile View */
          <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Mobile Tabs */}
            <div style={{
              display: 'flex',
              backgroundColor: 'var(--color-white)',
              borderBottom: '1px solid var(--color-gray-200)',
              boxShadow: 'var(--shadow-sm)',
              zIndex: 5
            }}>
              <button
                onClick={() => {
                  setMobileView('chat');
                  if ('vibrate' in navigator) navigator.vibrate(50);
                }}
                style={{
                  flex: 1,
                  padding: '14px 0',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  color: mobileView === 'chat' ? 'var(--color-brand-blue)' : 'var(--color-gray-500)',
                  borderBottom: `3px solid ${mobileView === 'chat' ? 'var(--color-brand-blue)' : 'transparent'}`,
                  fontWeight: 700,
                  transition: 'all 0.2s ease',
                  background: 'none',
                  border: 'none',
                  outline: 'none'
                }}
              >
                <MessageSquare size={18} />
                CHAT
              </button>
              <button
                onClick={() => {
                  setMobileView('map');
                  if ('vibrate' in navigator) navigator.vibrate(50);
                }}
                style={{
                  flex: 1,
                  padding: '14px 0',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  color: mobileView === 'map' ? 'var(--color-brand-blue)' : 'var(--color-gray-500)',
                  borderBottom: `3px solid ${mobileView === 'map' ? 'var(--color-brand-blue)' : 'transparent'}`,
                  fontWeight: 700,
                  transition: 'all 0.2s ease',
                  background: 'none',
                  border: 'none',
                  outline: 'none'
                }}
              >
                <MapIcon size={18} />
                MAP
                {routes.length > 0 && (
                  <span style={{
                    backgroundColor: 'var(--color-brand-blue)',
                    color: 'white',
                    borderRadius: '12px',
                    padding: '2px 8px',
                    fontSize: '10px',
                    marginLeft: '4px'
                  }}>{routes.length}</span>
                )}
              </button>
            </div>

            <div style={{ flex: 1, position: 'relative' }}>
              <AnimatePresence mode="wait">
                {mobileView === 'chat' ? (
                  <motion.div
                    key="chat"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    style={{ height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--color-white)' }}
                  >
                    <div style={{ flex: 1, overflowY: 'auto', paddingBottom: '20px' }}>
                      {messages.map(m => <MessageBubble key={m.id} message={m} />)}
                      {isTyping && <LoadingState />}
                      {!isTyping && messages.length > 1 && (
                        <div style={{ padding: '0 var(--spacing-sm)' }}>
                          {routes.map(r => (
                            <RouteCard
                              key={r.route.id}
                              rankedRoute={r}
                              isSelected={selectedRouteId === r.route.id}
                              onSelect={(id) => {
                                setSelectedRouteId(id);
                                setMobileView('map');
                                if ('vibrate' in navigator) navigator.vibrate(50);
                              }}
                            />
                          ))}
                        </div>
                      )}
                    </div>
                    <div style={{ paddingBottom: 'var(--bottom-nav-height)' }}>
                      <InputArea onSendMessage={handleSendMessage} />
                    </div>
                  </motion.div>
                ) : (
                  <motion.div
                    key="map"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    style={{ height: '100%', paddingBottom: isMobile ? 'var(--bottom-nav-height)' : 0 }}
                  >
                    <Map
                      routes={routes}
                      selectedRouteId={selectedRouteId}
                      setSelectedRouteId={setSelectedRouteId}
                      incidents={incidents}
                      phones={phones}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        )}

        {/* Floating SOS Button */}
        <motion.button
          onClick={() => {
            if ('vibrate' in navigator) navigator.vibrate([100, 50, 100]);
            alert('SOS activated! Sharing location with campus police and emergency contacts.');
          }}
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
          style={{
            position: 'absolute',
            bottom: isMobile ? 'calc(var(--bottom-nav-height) + 24px)' : '32px',
            right: '32px',
            width: '64px',
            height: '64px',
            borderRadius: 'var(--radius-full)',
            backgroundColor: 'var(--color-safety-100)',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 8px 32px rgba(211, 47, 47, 0.4)',
            zIndex: 2000,
            fontWeight: 800,
            fontSize: '14px',
            border: '3px solid white',
            cursor: 'pointer'
          }}
        >
          SOS
        </motion.button>
      </main>

      {isMobile && <BottomNav activeTab={activeTab} setActiveTab={setActiveTab} />}
    </div>
  );
};

export default App;
