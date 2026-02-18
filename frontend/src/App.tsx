import React, { useEffect, useCallback } from 'react';
import { useResponsive } from './hooks/useResponsive';
import { Header } from './components/layout/Header';
import { BottomNav } from './components/layout/BottomNav';
import { MessageBubble } from './components/chat/MessageBubble';
import { RouteCard } from './components/chat/RouteCard';
import { InputArea } from './components/chat/InputArea';
import { FloatingChat } from './components/chat/FloatingChat';
import { Map } from './components/map/Map';
import NewsPanel from './components/news/NewsPanel';
import { LoadingState } from './components/shared/LoadingState';
import { QuickActions } from './components/chat/QuickActions';
import { useStore } from './hooks/useStore';

import { motion, AnimatePresence } from 'framer-motion';
import { sendDispatchMessage, fetchRoutes } from './services/api';
import type { DispatchResponse } from './services/api';
import { DisambiguationDialog } from './components/chat/DisambiguationDialog';
import { TransportationModeSelector } from './components/chat/TransportationModeSelector';
import type { TransportationMode } from './types/disambiguation';

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
  const [disambiguationData, setDisambiguationData] = React.useState<DispatchResponse | null>(null);
  const [pendingDestination, setPendingDestination] = React.useState<string | null>(null);
  const [showModeSelector, setShowModeSelector] = React.useState(false);
  const [pendingMode, setPendingMode] = React.useState<'foot' | 'bike' | 'car' | 'bus'>('foot');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  // Fetch routes for a specific destination (called after disambiguation resolves or for direct destinations)
  const doFetchRoutes = useCallback(async (destination: string, mode: TransportationMode) => {
    const origin = userLocation ?? { latitude: 38.9446, longitude: -92.3266 };

    try {
      const routesPayload = await fetchRoutes({
        origin,
        destination,
        user_mode: 'student',
        priority: 'safety',
        time: 'current',
        concerns: [],
        transportation_mode: mode || 'foot',
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
  }, [userLocation, setRoutes, setSelectedRouteId, setIncidents, setEmergencyPhones, setIsTyping, addMessage]);

  const handleSendMessage = async (text: string) => {
    // Add user message
    addMessage({
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date()
    });

    setIsTyping(true);

    // Step 1: Call dispatch FIRST to check for disambiguation
    try {
      const dispatchResult = await sendDispatchMessage(text);

      // If disambiguation is needed, show the dialog and STOP (don't fetch routes yet)
      if (dispatchResult.response_type === 'disambiguation' && dispatchResult.options?.length) {
        setIsTyping(false);
        setDisambiguationData(dispatchResult);
        addMessage({
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: dispatchResult.question || 'Which location would you like to go to?',
          timestamp: new Date()
        });
        return; // Wait for user to pick a location
      }

      // No disambiguation needed — go to mode selection
      let destination = text;
      if (dispatchResult.response) {
        addMessage({
          id: (Date.now() + 2).toString(),
          role: 'assistant',
          content: dispatchResult.response,
          timestamp: new Date()
        });
        // If dispatchResult has a single match, use that as destination
        if (dispatchResult.category && dispatchResult.options && dispatchResult.options.length === 1) {
          destination = dispatchResult.options[0].name;
        }
      }
      setPendingDestination(destination);
      setShowModeSelector(true);
      setIsTyping(false);
      return;
    } catch (err) {
      console.error('Dispatch API error:', err);
      setIsTyping(false);
      // Optionally, fallback to old behavior
    }

  };

  // Handle disambiguation: user picked a specific location
  const handleDisambiguationSelect = async (location: { name: string; coordinates?: { latitude: number; longitude: number } }) => {
    setDisambiguationData(null);
    const destination = location.name;

    addMessage({
      id: Date.now().toString(),
      role: 'user',
      content: `Take me to ${destination}`,
      timestamp: new Date()
    });

    setPendingDestination(destination);
    setShowModeSelector(true);
  };

  // Handle mode selection
  const handleModeSelect = async (mode: 'foot' | 'bike' | 'car' | 'bus') => {
    setShowModeSelector(false);
    setPendingMode(mode);
    if (pendingDestination) {
      setIsTyping(true);
      await doFetchRoutes(pendingDestination, mode);
      setPendingDestination(null);
      setPendingMode('foot');
    }
  };

  const handleDisambiguationCancel = () => {
    setDisambiguationData(null);
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
        {/* Transportation Mode Selector Dialog */}
        {showModeSelector && (
          <div style={{ position: 'absolute', zIndex: 2000, left: 0, top: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.25)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ background: 'var(--color-bg-primary)', borderRadius: 16, boxShadow: '0 4px 32px rgba(0,0,0,0.15)', padding: 32, minWidth: 320 }}>
              <TransportationModeSelector onSelectMode={handleModeSelect} selectedMode={pendingMode || 'foot'} />
            </div>
          </div>
        )}
        {isDesktop ? (
          <div style={{ display: 'flex', height: '100%' }}>
            {/* Desktop Left Sidebar: Chat */}
            <FloatingChat
              onSendMessage={handleSendMessage}
              disambiguationData={disambiguationData?.response_type === 'disambiguation' ? (disambiguationData as any) : null}
              onDisambiguationSelect={handleDisambiguationSelect}
              onDisambiguationCancel={handleDisambiguationCancel}
            />

            {/* Desktop Right: Map */}
            <section style={{ flex: 1, position: 'relative' }}>
              <Map
                routes={routes}
                selectedRouteId={selectedRouteId}
                setSelectedRouteId={setSelectedRouteId}
                incidents={incidents}
                phones={phones}
              />
              {/* News Panel overlay */}
              <div style={{ position: 'absolute', top: '76px', right: '12px', zIndex: 1200, width: '320px' }}>
                <NewsPanel />
              </div>
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
                    style={{ height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--color-bg-primary)', overflow: 'hidden' }}
                  >
                    <div style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', WebkitOverflowScrolling: 'touch', paddingBottom: '20px' }}>
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

                    {/* Disambiguation Dialog for Mobile */}
                    {disambiguationData && (
                      <DisambiguationDialog
                        category={disambiguationData.category || ''}
                        question={disambiguationData.question || 'Which location?'}
                        options={disambiguationData.options || []}
                        onSelectLocation={handleDisambiguationSelect}
                        onCancel={handleDisambiguationCancel}
                      />
                    )}
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
                    {/* News Panel overlay (mobile) - compact icon with equal spacing to map controls */}
                    <div style={{ position: 'absolute', top: '120px', right: '12px', zIndex: 1200 }}>
                      <NewsPanel compact />
                    </div>
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
            // Handle home button - navigate to chat
            if (tab === 'home') {
              setActiveTab('chat');
              setMobileView('chat');
              if ('vibrate' in navigator) navigator.vibrate(50);
              return;
            }

            // Handle profile button - show coming soon popup
            if (tab === 'profile') {
              alert('Login and user features coming soon!');
              if ('vibrate' in navigator) navigator.vibrate(50);
              return;
            }

            // Handle other tabs normally
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
