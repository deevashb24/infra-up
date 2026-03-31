"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { MapPin, X, Info, Hammer, AlertTriangle, Moon, Sun, Map as MapIcon, Flag, LayoutDashboard, Loader2 } from "lucide-react";
import Link from "next/link";

// Pull API base URL from env so nothing hardcodes localhost.
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// Carto's glyph server returns PBF type 4 which MapLibre 5.x cannot parse.
// Fix: fetch the style JSON, replace the glyphs URL with the free MapLibre demo tiles server.
const GLYPH_URL = 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf';

async function fetchPatchedStyle(theme: "dark" | "light"): Promise<object> {
  const url = theme === "dark"
    ? 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json'
    : 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json';
  const res = await fetch(url);
  const style = await res.json();
  style.glyphs = GLYPH_URL;
  return style;
}

interface PermitProperties {
  id: string;
  title: string;
  permitType: string;
  status: string;
  startDate: string;
  endDate: string;
  contractor: string;
  project_authority: string;
  district: string;
  impactLevel: string;
  budget: number;
  completion_percent: number;
  cluster_id?: number;
}

interface AlertPayload {
  id: string;
  title: string;
  permit_type: string;
  district: string;
}

const DISTRICTS = [
  { name: "Lucknow", lng: 80.9462, lat: 26.8467 },
  { name: "Kanpur", lng: 80.3319, lat: 26.4499 },
  { name: "Varanasi", lng: 82.9739, lat: 25.3176 },
  { name: "Agra", lng: 78.0081, lat: 27.1767 },
  { name: "Prayagraj", lng: 81.8463, lat: 25.4358 },
  { name: "Meerut", lng: 77.7064, lat: 28.9845 },
  { name: "Ghaziabad", lng: 77.4538, lat: 28.6692 },
  { name: "Gorakhpur", lng: 83.3732, lat: 26.7606 },
  { name: "Aligarh", lng: 78.0880, lat: 27.8974 },
  { name: "Noida", lng: 77.3910, lat: 28.5355 }
];

const AUTHORITIES = ['LDA', 'LMC', 'NHAI', 'PWD_UP', 'UPLCL', 'Jal Nigam', 'UPSIDA', 'Smart City Lucknow'];

// Language Dictionary
const DICT = {
  EN: {
    road: 'Road Construction',
    water: 'Water Works',
    electric: 'Electrical Works',
    newProj: 'New Project Alert',
    highImpact: 'High Impact Highway Alert',
    report: 'Report Issue',
    district: 'District',
    status: 'Status',
    impactLevel: 'Impact Level',
    active: 'ACTIVE',
    pending: 'PENDING',
    filters: 'Live Filters',
    appTitle: 'UP Infra Intelligence',
    appSub: 'Live Govt Projects & Alerts',
    opArea: 'Operational Area',
    viewFull: 'View Full Project',
    submit: 'Submit Report',
    cancel: 'Cancel',
    describeIssue: 'Describe the safety hazard or violation...',
    affectedRoutes: 'Affected Routes',
    intersecting: 'This project intersects with 12 active commuter routes.',
    authority: 'Authority',
    reportTitle: 'Citizen Safety Report',
    budget: 'Budget',
    contractor: 'Contractor',
    progress: 'Progress',
    loadingData: 'Loading live project data...',
    errorData: 'Failed to load data. Showing cached view.',
  },
  HI: {
    road: 'सड़क निर्माण',
    water: 'जल कार्य',
    electric: 'बिजली कार्य',
    newProj: 'नई परियोजना',
    highImpact: 'उच्च प्रभाव चेतावनी',
    report: 'समस्या दर्ज करें',
    district: 'ज़िला',
    status: 'स्थिति',
    impactLevel: 'प्रभाव स्तर',
    active: 'सक्रिय',
    pending: 'लंबित',
    filters: 'लाइव फ़िल्टर',
    appTitle: 'यूपी इन्फ्रा इंटेलिजेंस',
    appSub: 'लाइव सरकारी प्रोजेक्ट और अलर्ट',
    opArea: 'संचालन क्षेत्र',
    viewFull: 'पूरा प्रोजेक्ट देखें',
    submit: 'रिपोर्ट सबमिट करें',
    cancel: 'रद्द करें',
    describeIssue: 'सुरक्षा खतरे या उल्लंघन का वर्णन करें...',
    affectedRoutes: 'प्रभावित मार्ग',
    intersecting: 'यह प्रोजेक्ट 12 सक्रिय मार्गों को प्रभावित करता है।',
    authority: 'प्राधिकरण',
    reportTitle: 'नागरिक सुरक्षा रिपोर्ट',
    budget: 'बजट',
    contractor: 'ठेकेदार',
    progress: 'प्रगति',
    loadingData: 'लाइव डेटा लोड हो रहा है...',
    errorData: 'डेटा लोड करने में विफल।',
  }
};

export default function InfraMap() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const addCustomLayersRef = useRef<() => void>(() => {});
  
  // State
  const [theme, setTheme] = useState<"light" | "dark">("dark");
  const [lang, setLang] = useState<"EN" | "HI">("EN");
  const [selectedPermit, setSelectedPermit] = useState<PermitProperties | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [selectedDistrict, setSelectedDistrict] = useState("Lucknow");
  
  // Live data from API
  const [permits, setPermits] = useState<GeoJSON.FeatureCollection | null>(null);
  const [dataLoading, setDataLoading] = useState(true);
  const [dataError, setDataError] = useState(false);
  
  // SSE Toast Notifications Stack
  const [toasts, setToasts] = useState<{id: number, data: AlertPayload}[]>([]);
  
  // Citizen Report Modal
  const [reportOpen, setReportOpen] = useState(false);
  const [reportText, setReportText] = useState("");
  const [reportStatus, setReportStatus] = useState<"idle" | "loading" | "success" | "error">("idle");

  const t = DICT[lang];

  // ── Fetch live projects from API ──────────────────────────────────────────
  useEffect(() => {
    let cancelled = false;
    async function fetchProjects() {
      setDataLoading(true);
      setDataError(false);
      try {
        const res = await fetch(`${API_BASE}/projects`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!cancelled) {
          setPermits(data);
          setDataLoading(false);
        }
      } catch (err) {
        console.error("Failed to fetch projects:", err);
        if (!cancelled) {
          setDataError(true);
          setDataLoading(false);
        }
      }
    }
    fetchProjects();
    return () => { cancelled = true; };
  }, []);

  // ── Update map source when data changes ───────────────────────────────────
  useEffect(() => {
    if (!mapRef.current || !permits) return;
    const map = mapRef.current;
    if (!map.isStyleLoaded()) return;
    const src = map.getSource('permits') as maplibregl.GeoJSONSource | undefined;
    if (src) {
      src.setData(permits);
    }
  }, [permits]);

  const addCustomLayers = useCallback(() => {
    const map = mapRef.current;
    if (!map) return;

    if (!map.getSource('up-boundary')) {
        map.addSource('up-boundary', { type: 'geojson', data: '/geodata/uttar_pradesh.geojson' });
        map.addLayer({ id: 'up-boundary-fill', type: 'fill', source: 'up-boundary', paint: { 'fill-color': '#f59e0b', 'fill-opacity': 0.05 } });
        map.addLayer({ id: 'up-boundary-line', type: 'line', source: 'up-boundary', paint: { 'line-color': '#f59e0b', 'line-width': 2.5, 'line-opacity': 0.8 } });
    }

    if (map.getSource('permits')) return;

    if (map.getSource('composite')) {
      const layers = map.getStyle().layers;
      let labelLayerId;
      for (let i = 0; i < layers.length; i++) {
          const layer = layers[i] as maplibregl.SymbolLayerSpecification;
          if (layer.type === 'symbol' && layer.layout && layer.layout['text-field']) {
              labelLayerId = layers[i].id;
              break;
          }
      }
      map.addLayer(
        {
          'id': '3d-buildings',
          'source': 'composite',
          'source-layer': 'building',
          'filter': ['==', 'extrude', 'true'],
          'type': 'fill-extrusion',
          'minzoom': 14,
          'paint': {
              'fill-extrusion-color': theme === "dark" ? '#334155' : '#e2e8f0',
              'fill-extrusion-height': ['get', 'height'],
              'fill-extrusion-base': ['get', 'min_height'],
              'fill-extrusion-opacity': 0.7
          }
        },
        labelLayerId
      );
    }

    // Use live data if available, otherwise empty collection
    const sourceData = permits || { type: "FeatureCollection" as const, features: [] };

    map.addSource('permits', {
      type: 'geojson',
      data: sourceData,
      cluster: true,
      clusterMaxZoom: 14,
      clusterRadius: 50
    });

    map.addLayer({
      id: 'clusters',
      type: 'circle',
      source: 'permits',
      filter: ['has', 'point_count'],
      paint: {
          'circle-color': ['step', ['get', 'point_count'], '#3b82f6', 10, '#8b5cf6', 30, '#f43f5e'],
          'circle-radius': ['step', ['get', 'point_count'], 20, 10, 30, 30, 40],
          'circle-opacity': 0.85,
          'circle-stroke-width': 2,
          'circle-stroke-color': '#fff'
      }
    });

    map.addLayer({
      id: 'cluster-count',
      type: 'symbol',
      source: 'permits',
      filter: ['has', 'point_count'],
      layout: { 'text-field': '{point_count_abbreviated}', 'text-font': ['Noto Sans Bold', 'Noto Sans Regular'], 'text-size': 14 },
      paint: { 'text-color': '#ffffff' }
    });

    map.addLayer({
      id: 'unclustered-point-halo',
      type: 'circle',
      source: 'permits',
      filter: ['!', ['has', 'point_count']],
      paint: {
          'circle-color': ['match', ['get', 'permitType'], 'CONSTRUCTION', '#f97316', 'ROAD', '#3b82f6', 'UTILITY', '#a855f7', '#94a3b8'],
          'circle-radius': 18,
          'circle-opacity': 0.2,
          'circle-blur': 0.4
      }
    });

    map.addLayer({
      id: 'unclustered-point',
      type: 'circle',
      source: 'permits',
      filter: ['!', ['has', 'point_count']],
      paint: {
          'circle-color': ['match', ['get', 'permitType'], 'CONSTRUCTION', '#f97316', 'ROAD', '#3b82f6', 'UTILITY', '#a855f7', '#94a3b8'],
          'circle-radius': 8,
          'circle-stroke-width': 2,
          'circle-stroke-color': '#fff',
          'circle-opacity': 0.9
      }
    });

  }, [theme, permits]);

  useEffect(() => {
    addCustomLayersRef.current = addCustomLayers;
  }, [addCustomLayers]);

  // Mount Map
  useEffect(() => {
    if (!mapContainer.current) return;
    if (mapRef.current) return;

    fetchPatchedStyle(theme).then(mapStyle => {
    if (!mapContainer.current) return;

    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: mapStyle as maplibregl.StyleSpecification,
      center: [80.9462, 26.8467], 
      zoom: 12, 
      pitch: 45, 
      bearing: -17.6,
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      antialias: true 
    });

    mapRef.current = map;

    map.once('load', () => setMapLoaded(true));
    map.on('style.load', () => addCustomLayersRef.current());

    map.on('click', 'clusters', async (e) => {
      const features = map.queryRenderedFeatures(e.point, { layers: ['clusters'] });
      if (!features.length) return;
      const clusterId = features[0].properties?.cluster_id;
      if (clusterId === undefined) return;
      try {
          const zoom = await (map.getSource('permits') as maplibregl.GeoJSONSource).getClusterExpansionZoom(clusterId);
          map.easeTo({ center: (features[0].geometry as GeoJSON.Point).coordinates as [number, number], zoom: zoom });
      } catch (err) {
          console.error(err);
      }
    });

    map.on('click', 'unclustered-point', (e) => {
      if (!e.features?.length) return;
      const feature = e.features[0];
      const coordinates = (feature.geometry as GeoJSON.Point).coordinates.slice() as [number, number];
      setSelectedPermit(feature.properties as unknown as PermitProperties);
      map.flyTo({ center: coordinates, zoom: 15, essential: true });
    });

    map.on('mouseenter', 'clusters', () => { map.getCanvas().style.cursor = 'pointer'; });
    map.on('mouseleave', 'clusters', () => { map.getCanvas().style.cursor = ''; });
    map.on('mouseenter', 'unclustered-point', () => { map.getCanvas().style.cursor = 'pointer'; });
    map.on('mouseleave', 'unclustered-point', () => { map.getCanvas().style.cursor = ''; });

    return () => {
      map.remove();
      mapRef.current = null;
      setMapLoaded(false);
    };
    }); // end fetchPatchedStyle.then()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Theme Sync
  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return;
    fetchPatchedStyle(theme).then(mapStyle => {
      if (!mapRef.current) return;
      mapRef.current.setStyle(mapStyle as maplibregl.StyleSpecification);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [theme, mapLoaded]);

  // SSE Alert Stream
  useEffect(() => {
    const eventSource = new EventSource(`${API_BASE}/api/alerts/stream`);
    eventSource.onmessage = (event) => {
        if (event.data === "keep-alive") return;
        try {
            const data = JSON.parse(event.data);
            const newToast = { id: Date.now(), data };
            setToasts(prev => [...prev, newToast]);
            // Re-fetch projects when a new one is added
            fetch(`${API_BASE}/projects`)
              .then(r => r.json())
              .then(d => setPermits(d))
              .catch(() => {});
            setTimeout(() => {
                setToasts(prev => prev.filter(t => t.id !== newToast.id));
            }, 6000);
        } catch {}
    };
    return () => eventSource.close();
  }, []);

  const handleDistrictChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const dName = e.target.value;
    setSelectedDistrict(dName);
    const districtInfo = DISTRICTS.find(d => d.name === dName);
    if (districtInfo && mapRef.current) {
        mapRef.current.flyTo({ center: [districtInfo.lng, districtInfo.lat], zoom: 11, essential: true });
    }
  };

  const handleReportSubmit = async () => {
    if (!reportText.trim()) return;
    setReportStatus("loading");
    const center = mapRef.current?.getCenter() ?? { lng: 80.9462, lat: 26.8467 };
    try {
      const res = await fetch(`${API_BASE}/reports`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          description: reportText,
          longitude: center.lng,
          latitude: center.lat,
        }),
      });
      if (res.ok) {
        setReportStatus("success");
        setReportText("");
        setTimeout(() => { setReportStatus("idle"); setReportOpen(false); }, 1500);
      } else {
        setReportStatus("error");
      }
    } catch {
      setReportStatus("error");
    }
  };

  const getTranslatedType = (typeRaw: string) => {
    if (typeRaw === 'ROAD') return t.road;
    if (typeRaw === 'UTILITY') return t.electric;
    if (typeRaw === 'CONSTRUCTION') return t.road;
    return typeRaw;
  };

  return (
    <div className={`relative w-full h-screen overflow-hidden ${theme === 'dark' ? 'dark text-slate-100' : 'text-slate-800'}`}>
      
      <div ref={mapContainer} className="absolute inset-0 w-full h-full bg-slate-100 dark:bg-slate-900 transition-colors" />
      
      {/* ===== GLOBAL LOADING STATE ===== */}
      {(!mapLoaded || dataLoading) && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-slate-900/80 backdrop-blur-md transition-opacity duration-1000">
           <div className="flex flex-col items-center gap-6">
              <div className="relative flex items-center justify-center">
                  <div className="absolute w-24 h-24 border-4 border-blue-500/20 rounded-full"></div>
                  <div className="absolute w-24 h-24 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                  <MapPin size={28} className="text-white animate-bounce" />
              </div>
              <p className="text-white font-black tracking-[0.2em] uppercase text-sm animate-pulse shadow-black drop-shadow-md">
                 {dataLoading ? t.loadingData : (lang === 'EN' ? 'Initializing Lucknow PostGIS...' : 'लखनऊ इन्फ्रास्ट्रक्चर लोड हो रहा है...')}
              </p>
           </div>
        </div>
      )}

      {/* ===== DATA ERROR BANNER ===== */}
      {dataError && !dataLoading && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 z-50 bg-rose-600/90 backdrop-blur-xl text-white px-6 py-3 rounded-xl shadow-lg flex items-center gap-3 font-bold text-sm">
          <AlertTriangle size={18} /> {t.errorData}
        </div>
      )}
      
      {/* NOTIFICATIONS STACK (SSE Toasts) */}
      <div className="absolute top-20 right-6 z-50 flex flex-col gap-3 pointer-events-none">
        {toasts.map((toast) => (
            <div key={toast.id} className={`bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl p-4 rounded-xl shadow-2xl border-l-4 border-blue-500 w-80 transform transition-all duration-500 ease-out translate-x-0 opacity-100`}>
                <h4 className="font-bold text-sm text-slate-800 dark:text-white flex items-center gap-2 tracking-wide">
                    <span className="relative flex h-3 w-3">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
                    </span>
                    {t.newProj}
                </h4>
                <p className="text-xs text-slate-600 dark:text-slate-300 mt-2 font-medium leading-relaxed">{toast.data.title}</p>
                <div className="flex gap-2 items-center mt-3">
                  <span className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded-md text-[10px] text-slate-500 dark:text-slate-400 font-bold uppercase tracking-widest">{toast.data.district}</span>
                  <span className="px-2 py-1 bg-blue-50 dark:bg-blue-900/20 rounded-md text-[10px] text-blue-600 dark:text-blue-400 font-bold uppercase tracking-widest">{getTranslatedType(toast.data.permit_type || 'ROAD')}</span>
                </div>
            </div>
        ))}
      </div>

      {/* ===== HUD Top Left ===== */}
      <div className="absolute top-6 left-6 z-10 hidden lg:flex flex-col gap-4 w-72 pointer-events-none">
        <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl p-4 rounded-2xl shadow-xl border border-white/20 dark:border-slate-700/50 flex items-center gap-3 transition-colors pointer-events-auto">
            <div className="p-2 bg-blue-500 rounded-lg text-white">
                <MapPin size={24} />
            </div>
            <div>
                <h1 className="font-bold text-lg leading-tight tracking-tight font-noto-deva">{t.appTitle}</h1>
                <p className="text-xs text-slate-500 dark:text-slate-400 font-medium tracking-wide">{t.appSub}</p>
            </div>
        </div>

        <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl p-4 rounded-2xl shadow-xl border border-white/20 dark:border-slate-700/50 transition-colors flex flex-col gap-4 pointer-events-auto">
            <div>
                <h3 className="text-xs uppercase font-bold text-slate-400 tracking-wider mb-2 flex items-center gap-2"><MapIcon size={14}/> {t.opArea}</h3>
                <select 
                    value={selectedDistrict}
                    onChange={handleDistrictChange}
                    className="w-full bg-slate-100 dark:bg-slate-800/80 p-2.5 rounded-lg text-sm font-semibold outline-none border border-slate-200 dark:border-slate-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all cursor-pointer"
                >
                    {DISTRICTS.map(d => (
                        <option key={d.name} value={d.name}>{d.name}</option>
                    ))}
                </select>
            </div>
            <div className="h-px w-full bg-slate-200 dark:bg-slate-700/50 my-1"></div>
            <div>
                <h3 className="text-xs uppercase font-bold text-slate-400 tracking-wider mb-3">{t.filters}</h3>
                <div className="flex flex-col gap-3 text-sm font-medium">
                    <div className="flex items-center gap-2 cursor-pointer hover:opacity-80">
                        <div className="w-3 h-3 rounded-full bg-orange-500 shadow-[0_0_10px_rgba(249,115,22,0.6)]"></div>
                        {t.road}
                    </div>
                    <div className="flex items-center gap-2 cursor-pointer hover:opacity-80">
                        <div className="w-3 h-3 rounded-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.6)]"></div>
                        {t.water}
                    </div>
                    <div className="flex items-center gap-2 cursor-pointer hover:opacity-80">
                        <div className="w-3 h-3 rounded-full bg-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.6)]"></div>
                        {t.electric}
                    </div>
                </div>
            </div>
        </div>
      </div>

      {/* ===== Floating Top Right Controls ===== */}
      <div className="absolute top-4 right-4 sm:top-6 sm:right-6 z-20 flex gap-2 flex-col sm:flex-row">
        <Link
            href="/dashboard"
            className="px-4 py-2 bg-blue-600/90 hover:bg-blue-500 backdrop-blur-xl rounded-xl shadow-lg border border-blue-500/40 transition-all active:scale-95 flex items-center justify-center gap-2 font-bold text-sm text-white"
            aria-label="Open Dashboard"
        >
            <LayoutDashboard size={16} />
            <span className="hidden sm:inline">Dashboard</span>
        </Link>
        <button 
            onClick={() => setLang(lang === 'EN' ? 'HI' : 'EN')}
            className="px-4 py-2 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl rounded-xl shadow-lg border border-white/20 dark:border-slate-700/50 hover:bg-white dark:hover:bg-slate-800 transition-all active:scale-95 flex items-center justify-center font-bold text-sm"
            aria-label="Toggle Language"
        >
            {lang === 'EN' ? 'हिंदी' : 'EN'}
        </button>
        <button 
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            className="p-3 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl rounded-xl shadow-lg border border-white/20 dark:border-slate-700/50 hover:bg-white dark:hover:bg-slate-800 transition-all active:scale-95 flex items-center justify-center"
            aria-label="Toggle Theme"
        >
            {theme === 'light' ? <Moon size={20} className="text-slate-700"/> : <Sun size={20} className="text-yellow-400"/>}
        </button>
      </div>

      {/* ===== Bottom Floating Action (Report Issue) ===== */}
      <div className="absolute bottom-10 left-1/2 transform -translate-x-1/2 z-10">
          <button 
            onClick={() => setReportOpen(true)}
            className="flex items-center gap-2 bg-rose-600 hover:bg-rose-500 text-white px-6 py-3 rounded-full shadow-lg shadow-rose-600/30 font-bold tracking-wide transition-all active:scale-95 border border-rose-500"
          >
              <Flag size={18} /> {t.report}
          </button>
      </div>

      {/* ===== Citizen Safety Report Modal ===== */}
      {reportOpen && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
              <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-2xl w-full max-w-md border border-slate-200 dark:border-slate-800">
                  <div className="flex justify-between items-center mb-4">
                      <h2 className="text-lg font-bold flex items-center gap-2"><AlertTriangle className="text-rose-500"/> {t.reportTitle}</h2>
                      <button onClick={() => setReportOpen(false)} className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full"><X size={20}/></button>
                  </div>
                  <textarea 
                    value={reportText}
                    onChange={(e) => setReportText(e.target.value)}
                    placeholder={t.describeIssue}
                    className="w-full h-32 p-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20 resize-none text-sm font-medium"
                  ></textarea>
                  {reportStatus === "error" && (
                    <p className="text-rose-500 text-xs font-bold mt-2">Submission failed. Please try again.</p>
                  )}
                  {reportStatus === "success" && (
                    <p className="text-emerald-500 text-xs font-bold mt-2">Report submitted successfully!</p>
                  )}
                  <div className="mt-6 flex gap-3">
                      <button
                        onClick={() => { setReportOpen(false); setReportStatus("idle"); setReportText(""); }}
                        className="flex-1 py-3 px-4 rounded-xl font-bold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition"
                      >
                          {t.cancel}
                      </button>
                      <button
                        onClick={handleReportSubmit}
                        disabled={reportStatus === "loading" || !reportText.trim()}
                        className="flex-1 py-3 px-4 rounded-xl font-bold bg-rose-600 hover:bg-rose-500 text-white shadow-lg shadow-rose-500/20 transition disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                          {reportStatus === "loading" ? "Submitting..." : t.submit}
                      </button>
                  </div>
              </div>
          </div>
      )}


      {/* ===== Slide-out Sidebar Panel for Selected Permit ===== */}
      <div 
        className={`absolute top-0 right-0 h-full w-full md:max-w-[400px] bg-white/95 dark:bg-slate-900/95 backdrop-blur-3xl shadow-[0_0_40px_rgba(0,0,0,0.3)] border-l border-white/20 dark:border-slate-700/50 transform transition-all duration-700 cubic-bezier(0.16, 1, 0.3, 1) z-40 overflow-y-auto ${selectedPermit ? 'translate-x-0 opacity-100 object-top' : 'translate-x-full opacity-0'}`}
      >
        {selectedPermit && (
          <div className="p-6 h-full flex flex-col pt-24 md:pt-6">
            <div className="flex justify-between items-start mb-6">
                <div>
                    <span className="inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-400 mb-2 transition-colors">
                        {getTranslatedType(selectedPermit.permitType)}
                    </span>
                    <h2 className="text-2xl font-bold tracking-tight text-slate-800 dark:text-white transition-colors">
                        {selectedPermit.title}
                    </h2>
                    <p className="text-sm text-slate-500 dark:text-slate-400 flex items-center gap-1 mt-1 transition-colors">
                        <Info size={14} /> ID: {selectedPermit.id?.substring(0, 8)}...
                    </p>
                </div>
                <button onClick={() => setSelectedPermit(null)} className="p-2 bg-slate-100 dark:bg-slate-800 rounded-full hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">
                    <X size={20} />
                </button>
            </div>

            <div className="space-y-4 flex-grow">
                <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-100 dark:border-slate-700/50 transition-colors">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                        <Hammer size={14} /> Project Details
                    </h4>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1 transition-colors">{t.authority}</p>
                            <p className="font-semibold">{selectedPermit.project_authority}</p>
                        </div>
                        <div>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1 transition-colors">{t.district}</p>
                            <p className="font-semibold text-slate-800 dark:text-white">{selectedPermit.district}</p>
                        </div>
                        <div>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1 transition-colors">{t.status}</p>
                            <p className="font-semibold flex items-center gap-2">
                                <span className={`w-2 h-2 rounded-full ${selectedPermit.status === 'ACTIVE' ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
                                {selectedPermit.status === 'ACTIVE' ? t.active : t.pending}
                            </p>
                        </div>
                        <div>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1 transition-colors">{t.impactLevel}</p>
                            <p className="font-semibold text-rose-500">{selectedPermit.impactLevel}</p>
                        </div>
                        <div>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1 transition-colors">{t.budget}</p>
                            <p className="font-semibold text-emerald-600 dark:text-emerald-400">₹{selectedPermit.budget} Cr</p>
                        </div>
                        <div>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1 transition-colors">{t.contractor}</p>
                            <p className="font-semibold text-sm">{selectedPermit.contractor || selectedPermit.project_authority}</p>
                        </div>
                    </div>
                </div>

                {/* Progress Bar */}
                {selectedPermit.completion_percent > 0 && (
                  <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-100 dark:border-slate-700/50">
                    <div className="flex justify-between items-end mb-2">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest">{t.progress}</h4>
                      <span className="text-lg font-black text-blue-600 dark:text-blue-400">{selectedPermit.completion_percent}%</span>
                    </div>
                    <div className="w-full h-3 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full transition-all duration-1000" style={{ width: `${selectedPermit.completion_percent}%` }}></div>
                    </div>
                  </div>
                )}

                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-100 dark:border-blue-800/30 transition-colors">
                     <h4 className="text-xs font-bold text-blue-500 dark:text-blue-400 uppercase tracking-widest mb-2 flex items-center gap-2 transition-colors">
                        <AlertTriangle size={14} /> {t.affectedRoutes}
                    </h4>
                    <p className="text-sm text-slate-700 dark:text-slate-300 transition-colors">{t.intersecting}</p>
                </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-200 dark:border-slate-700/50 flex gap-3 transition-colors">
                <Link href={`/projects/${selectedPermit.id}`} className="flex-1 bg-blue-600 hover:bg-blue-500 dark:hover:bg-blue-700 text-white py-3 px-4 rounded-xl font-medium shadow-lg shadow-blue-500/20 transition-all active:scale-95 text-center">
                    {t.viewFull}
                </Link>
            </div>
          </div>
        )}
      </div>

    </div>
  );
}
