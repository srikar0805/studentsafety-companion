import React, { useEffect } from 'react';
import { useResponsive } from './hooks/useResponsive';
import { Header } from './components/layout/Header';
import { BottomNav } from './components/layout/BottomNav';
import { MessageBubble } from './components/chat/MessageBubble';
import { RouteCard } from './components/chat/RouteCard';
import { InputArea } from './components/chat/InputArea';
import { FloatingChat } from './components/chat/FloatingChat';
import { Map } from './components/map/Map';
import { LoadingState } from './components/shared/LoadingState';
import { QuickActions } from './components/chat/QuickActions';
import { useStore } from './hooks/useStore';
import { MessageSquare, Map as MapIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { sendDispatchMessage, fetchRoutes } from './services/api';

const App: React.FC = () => {
  const { isMobile, isDesktop } = useResponsive();
  const {
    messages, addMessage, isTyping, setIsTyping,
    routes, selectedRouteId, setSelectedRouteId, setRoutes,
    isDarkMode, toggleDarkMode,
    incidents,
    emergencyPhones: phones,
    setIncidents,
    setEmergencyPhones,
    userLocation
  } = useStore();

  const [activeTab, setActiveTab] = React.useState<'home' | 'chat' | 'map' | 'history' | 'profile'>('chat');
  const [mobileView, setMobileView] = React.useState<'chat' | 'map'>('chat');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  const handleSendMessage = async (text: string) => {
    // Add user message
    addMessage({
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date()
    });

    // Show loading state
    setIsTyping(true);

    const origin = userLocation ?? { latitude: 38.9446, longitude: -92.3266 };

    // 1. Fetch routes first (fast ~2s) — show results immediately
    try {
      const routesPayload = await fetchRoutes({
        origin,
        destination: text,
        user_mode: 'student',
        priority: 'safety',
        time: 'current',
        concerns: []
      });

      const rankedRoutes = routesPayload.recommendation.routes;
      setRoutes(rankedRoutes);
      setSelectedRouteId(rankedRoutes.length ? rankedRoutes[0].route.id : null);
      setIncidents(routesPayload.incidents);
      setEmergencyPhones(
        routesPayload.emergency_phones.map((phone, index) => ({
          id: `phone-${index + 1}`,
          location: phone,
          name: 'Emergency Phone'
        }))
      );

      // Show route explanation immediately
      setIsTyping(false);
      addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: routesPayload.recommendation.explanation,
        timestamp: new Date()
      });
    } catch (routeError) {
      console.error('Routes API error:', routeError);
      setIsTyping(false);
      addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Sorry, I couldn't generate routes: ${routeError instanceof Error ? routeError.message : 'Unknown error'}. Please try again.`,
        timestamp: new Date()
      });
    }

    // 2. Fetch AI dispatch response in background (slow ~20s) — append when ready
    sendDispatchMessage(text)
      .then((dispatchResult) => {
        if (dispatchResult.response) {
          addMessage({
            id: (Date.now() + 2).toString(),
            role: 'assistant',
            content: dispatchResult.response,
            timestamp: new Date()
          });
        }
      })
      .catch((err) => {
        console.error('Dispatch API error:', err);
      });
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
            <FloatingChat onSendMessage={handleSendMessage} />

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
          <div style={{ height: '100%', display: 'flex', flexDirection: 'column', paddingTop: '64px' }}>
            <div style={{ flex: 1, position: 'relative' }}>
              <AnimatePresence mode="wait">
                {mobileView === 'chat' ? (
                  <motion.div
                    key="chat"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    style={{ height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--color-bg-primary)' }}
                  >
                    <div style={{ flex: 1, overflowY: 'auto', paddingBottom: '20px' }}>
                      {messages.map(m => <MessageBubble key={m.id} message={m} />)}

                      {/* Show Quick Actions if only the initial greeting exists */}
                      {!isTyping && messages.length === 1 && (
                        <QuickActions onAction={handleSendMessage} />
                      )}

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
                                setActiveTab('map');
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

        {/* Floating SOS Button - Desktop Only */}
        {!isMobile && (
          <motion.button
            onClick={() => {
              if ('vibrate' in navigator) navigator.vibrate([100, 50, 100]);
              alert('SOS activated! Sharing location with campus police and emergency contacts.');
            }}
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            style={{
              position: 'absolute',
              bottom: '32px',
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
        )}
      </main>

      {isMobile && (
        <BottomNav
          activeTab={activeTab}
          onSOS={() => {
            if ('vibrate' in navigator) navigator.vibrate([100, 50, 100]);
            alert('SOS activated! Sharing location with campus police and emergency contacts.');
          }}
          setActiveTab={(tab) => {
            setActiveTab(tab);
            if (tab === 'chat') setMobileView('chat');
            if (tab === 'map') setMobileView('map');
            if ('vibrate' in navigator) navigator.vibrate(50);
          }}
        />
      )}
    </div>
  );
};

export default App;
