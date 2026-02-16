import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Map as MapIcon, AlertCircle, Phone, Shield } from 'lucide-react';

export const MapLegend: React.FC = () => {
    const [isCollapsed, setIsCollapsed] = useState(false);

    return (
        <div style={{
            position: 'absolute',
        }}>
            <div
                onClick={() => setIsCollapsed(!isCollapsed)}
                style={{
                    padding: '12px 16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer',
                                </div>
                            ))}
                        </div>
                    </div>

                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
