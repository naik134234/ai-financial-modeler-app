"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import {
    FileSpreadsheet,
    Building2,
    TrendingUp,
    Zap,
    Download,
    Search,
    ChevronRight,
    AlertCircle,
    CheckCircle,
    Loader2,
    BarChart3,
    DollarSign,
    LineChart,
    Sparkles,
    Database,
    Upload,
    Filter,
    ChevronDown,
    X,
    PieChart,
    Table,
    Sun,
    Moon,
    History,
    FileText,
    Presentation,
    Code,
    Save,
    FolderOpen,
} from "lucide-react";

// Types
interface Stock {
    symbol: string;
    name: string;
    sector: string;
    sector_code?: string;
}

interface CompanyInfo {
    symbol: string;
    name: string;
    sector: string;
    industry: string;
    market_cap: number | null;
    current_price: number | null;
}

interface JobStatus {
    job_id: string;
    status: string;
    progress: number;
    message: string;
    company_name?: string;
    industry?: string;
    download_url?: string;
    filename?: string;
    validation?: {
        is_valid: boolean;
        errors: any[];
    };
}

interface JobHistoryItem {
    id: string;
    company_name: string;
    industry?: string;
    status: string;
    created_at: string;
    file_path?: string;
}

interface ExportFormat {
    id: string;
    name: string;
    extension: string | null;
    available: boolean;
    description: string;
}

interface MonteCarloResults {
    job_id: string;
    company_name: string;
    simulations: number;
    results: {
        statistics: {
            share_price: { mean: number; median: number; std: number; min: number; max: number; p5: number; p25: number; p75: number; p95: number };
            enterprise_value?: { mean: number; median: number };
            equity_value?: { mean: number; median: number };
        };
        histogram?: { bins: number[]; counts: number[] };
        probability_above_current?: number;
        confidence_interval_90?: [number, number];
    };
}


// API Functions
// API Configuration
// Production: Uses relative path (hits Vercel backend via rewrites)
// Development: Hits local Python server
const API_BASE = process.env.NODE_ENV === 'production'
    ? ""
    : "http://localhost:8000";

async function fetchAllStocks(sector?: string): Promise<{ stocks: Stock[]; count: number }> {
    const url = sector ? `${API_BASE}/api/stocks?sector=${sector}` : `${API_BASE}/api/stocks`;
    const response = await fetch(url);
    if (!response.ok) throw new Error("Failed to fetch stocks");
    return response.json();
}

async function searchStocks(query: string): Promise<{ results: Stock[] }> {
    const response = await fetch(`${API_BASE}/api/stocks/search/${query}`);
    if (!response.ok) throw new Error("Search failed");
    return response.json();
}

async function fetchSectors(): Promise<{ sectors: string[] }> {
    const response = await fetch(`${API_BASE}/api/sectors`);
    if (!response.ok) throw new Error("Failed to fetch sectors");
    return response.json();
}

async function generateModel(symbol: string, forecastYears: number): Promise<{ job_id: string }> {
    const response = await fetch(`${API_BASE}/api/model/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            symbol,
            exchange: "NSE",
            forecast_years: forecastYears,
            model_types: ["three_statement", "dcf"],
        }),
    });
    if (!response.ok) throw new Error("Failed to start model generation");
    return response.json();
}

async function generateRawModel(data: RawModelData): Promise<{ job_id: string }> {
    const response = await fetch(`${API_BASE}/api/model/generate-raw`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Failed to start raw model generation");
    return response.json();
}

interface LBOModelData {
    symbol: string;
    exchange: string;
    holding_period: number;
    entry_multiple: number;
    exit_multiple: number;
    senior_debt_multiple: number;
    senior_interest_rate: number;
    mezz_debt_multiple: number;
    mezz_interest_rate: number;
    sub_debt_multiple: number;
    sub_interest_rate: number;
    revenue_growth: number;
    ebitda_margin: number;
}

async function generateLBOModel(data: LBOModelData): Promise<{ job_id: string }> {
    const response = await fetch(`${API_BASE}/api/model/generate-lbo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Failed to start LBO model generation");
    return response.json();
}

interface MAModelData {
    acquirer_symbol: string;
    target_symbol: string;
    exchange: string;
    offer_premium: number;
    percent_stock: number;
    percent_cash: number;
    synergies_revenue: number;
    synergies_cost: number;
    acquirer_growth_rate: number;
    target_growth_rate: number;
}

async function generateMAModel(data: MAModelData): Promise<{ job_id: string }> {
    const response = await fetch(`${API_BASE}/api/model/generate-ma`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Failed to start M&A model generation");
    return response.json();
}

interface LBOTemplate {
    id: string;
    name: string;
    description: string;
    icon: string;
    assumptions: {
        holding_period: number;
        entry_multiple: number;
        exit_multiple: number;
        senior_debt_multiple: number;
        senior_interest_rate: number;
        mezz_debt_multiple: number;
        mezz_interest_rate: number;
        sub_debt_multiple: number;
        sub_interest_rate: number;
        revenue_growth: number;
        ebitda_margin: number;
    };
    key_metrics: string[];
}

async function fetchLBOTemplates(): Promise<{ templates: LBOTemplate[] }> {
    const response = await fetch(`${API_BASE}/api/templates/lbo`);
    if (!response.ok) return { templates: [] };
    return response.json();
}

async function downloadExportFile(jobId: string, format: "pdf" | "pptx"): Promise<void> {
    const response = await fetch(`${API_BASE}/api/export/${jobId}/${format}`);
    if (!response.ok) throw new Error(`Export failed: ${format}`);

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `model.${format}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
}

async function uploadExcelFile(
    file: File,
    companyName: string,
    industry: string,
    forecastYears: number
): Promise<{ job_id: string }> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("company_name", companyName);
    formData.append("industry", industry);
    formData.append("forecast_years", forecastYears.toString());

    const response = await fetch(`${API_BASE}/api/model/upload-excel`, {
        method: "POST",
        body: formData,
    });
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed: ${response.status}`);
    }
    return response.json();
}

async function getJobStatus(jobId: string): Promise<JobStatus> {
    const response = await fetch(`${API_BASE}/api/job/${jobId}`);
    if (!response.ok) throw new Error("Failed to get job status");
    return response.json();
}

async function getJobHistory(limit: number = 20): Promise<{ jobs: JobHistoryItem[] }> {
    const response = await fetch(`${API_BASE}/api/jobs/history?limit=${limit}`);
    if (!response.ok) return { jobs: [] };
    return response.json();
}

async function getExportFormats(): Promise<{ formats: ExportFormat[] }> {
    const response = await fetch(`${API_BASE}/api/export/formats`);
    if (!response.ok) return { formats: [] };
    return response.json();
}

async function runMonteCarloSimulation(jobId: string, simulations: number = 1000): Promise<MonteCarloResults> {
    const response = await fetch(`${API_BASE}/api/analysis/monte-carlo/${jobId}?simulations=${simulations}`);
    if (!response.ok) throw new Error("Monte Carlo simulation failed");
    return response.json();
}

async function downloadExport(jobId: string, format: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api/export/${jobId}/${format}`);
    if (!response.ok) throw new Error(`Export failed: ${format}`);

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `model.${format}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
}

interface RawModelData {
    company_name: string;
    industry: string;
    forecast_years: number;
    historical_data: {
        income_statement?: { revenue?: number; ebitda?: number; net_income?: number };
        balance_sheet?: { total_assets?: number; total_liabilities?: number };
    };
    assumptions: {
        revenue_growth?: number;
        ebitda_margin?: number;
        tax_rate?: number;
    };
}

// Feature cards data
const FEATURES = [
    {
        icon: Zap,
        title: "AI-Powered",
        description: "Gemini AI classifies industry & builds model logic",
        color: "from-yellow-500 to-orange-500",
    },
    {
        icon: FileSpreadsheet,
        title: "Real Excel Formulas",
        description: "Linked cells, charts, sensitivity analysis",
        color: "from-green-500 to-emerald-500",
    },
    {
        icon: Building2,
        title: "150+ Stocks",
        description: "Power, Banking, FMCG, IT, Pharma & more",
        color: "from-blue-500 to-cyan-500",
    },
    {
        icon: TrendingUp,
        title: "Advanced DCF",
        description: "WACC, scenarios, dashboard with charts",
        color: "from-purple-500 to-pink-500",
    },
];

const SECTOR_COLORS: { [key: string]: string } = {
    power: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    banking: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    it: "bg-purple-500/20 text-purple-400 border-purple-500/30",
    pharma: "bg-green-500/20 text-green-400 border-green-500/30",
    fmcg: "bg-orange-500/20 text-orange-400 border-orange-500/30",
    auto: "bg-red-500/20 text-red-400 border-red-500/30",
    metals: "bg-slate-500/20 text-slate-400 border-slate-500/30",
    oil_gas: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    cement: "bg-stone-500/20 text-stone-400 border-stone-500/30",
    infra: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
    nbfc: "bg-indigo-500/20 text-indigo-400 border-indigo-500/30",
    telecom: "bg-pink-500/20 text-pink-400 border-pink-500/30",
    chemicals: "bg-lime-500/20 text-lime-400 border-lime-500/30",
    consumer: "bg-rose-500/20 text-rose-400 border-rose-500/30",
};

type TabType = "stocks" | "excel" | "lbo" | "ma" | "compare";

export default function Home() {
    const [activeTab, setActiveTab] = useState<TabType>("stocks");
    const [stocks, setStocks] = useState<Stock[]>([]);
    const [sectors, setSectors] = useState<string[]>([]);
    const [selectedSector, setSelectedSector] = useState<string>("");
    const [searchQuery, setSearchQuery] = useState("");
    const [searchResults, setSearchResults] = useState<Stock[]>([]);

    const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
    const [forecastYears, setForecastYears] = useState(5);
    const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    // Monte Carlo simulation state
    const [monteCarloResults, setMonteCarloResults] = useState<MonteCarloResults | null>(null);
    const [isRunningMonteCarlo, setIsRunningMonteCarlo] = useState(false);

    // Excel file upload state
    const [excelFile, setExcelFile] = useState<File | null>(null);
    const [excelCompanyName, setExcelCompanyName] = useState("");
    const [excelIndustry, setExcelIndustry] = useState("general");
    const [isDragging, setIsDragging] = useState(false);

    // Persistence State
    const [showSaveModal, setShowSaveModal] = useState(false);
    const [showLoadModal, setShowLoadModal] = useState(false);
    const [projectName, setProjectName] = useState("");
    const [savedProjects, setSavedProjects] = useState<any[]>([]);

    const saveProject = async () => {
        if (!projectName.trim()) return;
        try {
            await fetch(`${API_BASE}/api/projects`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: projectName,
                    project_type: activeTab,
                    configuration: {
                        selectedStock,
                        lboAssumptions,
                        maAssumptions,
                        searchQuery,
                        activeTab
                    }
                })
            });
            setShowSaveModal(false);
            setProjectName("");
            alert("Project saved!");
        } catch (e) {
            console.error(e);
            alert("Failed to save project");
        }
    };

    const loadProjects = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/projects`);
            const data = await res.json();
            setSavedProjects(data.projects || []);
            setShowLoadModal(true);
        } catch (e) {
            console.error(e);
        }
    };

    const loadProject = (project: any) => {
        try {
            const config = project.configuration;
            if (config.activeTab) setActiveTab(config.activeTab);
            if (config.selectedStock) setSelectedStock(config.selectedStock);
            if (config.lboAssumptions) setLboAssumptions(config.lboAssumptions);
            if (config.maAssumptions) setMaAssumptions(config.maAssumptions);
            if (config.searchQuery) setSearchQuery(config.searchQuery);
            setShowLoadModal(false);
        } catch (e) {
            console.error("Error applying project config", e);
        }
    };

    // LBO model state
    const [lboAssumptions, setLboAssumptions] = useState({
        holding_period: 5,
        entry_multiple: 8.0,
        exit_multiple: 8.0,
        senior_debt_multiple: 3.0,
        senior_interest_rate: 0.08,
        mezz_debt_multiple: 1.5,
        mezz_interest_rate: 0.12,
        sub_debt_multiple: 0.5,
        sub_interest_rate: 0.14,
        revenue_growth: 0.08,
        ebitda_margin: 0.25,
    });

    // M&A model state
    const [acquirerStock, setAcquirerStock] = useState<Stock | null>(null);
    const [targetStock, setTargetStock] = useState<Stock | null>(null);
    const [maSearchQuery, setMaSearchQuery] = useState("");
    const [maSearchResults, setMaSearchResults] = useState<Stock[]>([]);
    const [maSearchType, setMaSearchType] = useState<"acquirer" | "target">("acquirer");
    const [maAssumptions, setMaAssumptions] = useState({
        offer_premium: 0.25,
        percent_stock: 0.50,
        percent_cash: 0.50,
        synergies_revenue: 0,
        synergies_cost: 0,
        acquirer_growth_rate: 0.05,
        target_growth_rate: 0.05,
    });

    // Enhancement features state
    const [showChat, setShowChat] = useState(false);
    const [chatMessage, setChatMessage] = useState("");
    const [chatHistory, setChatHistory] = useState<{ role: string; content: string }[]>([]);
    const [isChatting, setIsChatting] = useState(false);
    const [sensitivityData, setSensitivityData] = useState<any>(null);
    const [footballFieldData, setFootballFieldData] = useState<any>(null);
    const [showFootballField, setShowFootballField] = useState(false);
    const [templates, setTemplates] = useState<any>({});
    const [usStocks, setUsStocks] = useState<Stock[]>([]);
    const [marketFilter, setMarketFilter] = useState<"all" | "india" | "us">("all");

    // Fetch templates on mount
    useEffect(() => {
        fetch(`${API_BASE}/templates`)
            .then(res => res.json())
            .then(data => setTemplates(data.templates || {}))
            .catch(err => console.log("Templates not loaded"));
    }, []);

    // Chat with AI about model
    const sendChatMessage = async () => {
        if (!chatMessage.trim() || !jobStatus?.job_id) return;

        const userMsg = chatMessage;
        setChatMessage("");
        setChatHistory(prev => [...prev, { role: "user", content: userMsg }]);
        setIsChatting(true);

        try {
            const response = await fetch(`${API_BASE}/chat/${jobStatus.job_id}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userMsg, history: chatHistory })
            });
            const data = await response.json();
            setChatHistory(prev => [...prev, { role: "assistant", content: data.response }]);
        } catch (err) {
            setChatHistory(prev => [...prev, { role: "assistant", content: "Sorry, I had trouble responding." }]);
        } finally {
            setIsChatting(false);
        }
    };

    // Fetch sensitivity analysis
    const fetchSensitivity = async () => {
        if (!jobStatus?.job_id) return;
        try {
            const response = await fetch(`${API_BASE}/analysis/sensitivity/${jobStatus.job_id}`);
            const data = await response.json();
            setSensitivityData(data.sensitivity);
        } catch (err) {
            console.error("Sensitivity fetch error:", err);
        }
    };

    // Fetch football field
    const fetchFootballField = async () => {
        if (!jobStatus?.job_id) return;
        try {
            const response = await fetch(`${API_BASE}/analysis/football-field/${jobStatus.job_id}`);
            const data = await response.json();
            setFootballFieldData(data.football_field);
            setShowFootballField(true);
        } catch (err) {
            console.error("Football field fetch error:", err);
        }
    };

    // Fetch US stocks
    const fetchUsStocks = async (query: string) => {
        try {
            const response = await fetch(`${API_BASE}/stocks/us?search=${query}&limit=20`);
            const data = await response.json();
            setUsStocks(data.stocks || []);
        } catch (err) {
            console.log("US stocks not available");
        }
    };


    // Validation warnings for LBO/M&A inputs
    const validationWarnings = {
        lbo: {
            ebitda_margin: lboAssumptions.ebitda_margin > 0.40
                ? "⚠️ EBITDA margin above 40% is unusually high for most industries"
                : lboAssumptions.ebitda_margin < 0.10
                    ? "⚠️ EBITDA margin below 10% may indicate challenging economics"
                    : null,
            entry_multiple: lboAssumptions.entry_multiple > 15
                ? "⚠️ Entry multiple above 15x is very high for LBO transactions"
                : lboAssumptions.entry_multiple < 5
                    ? "💡 Entry multiple below 5x indicates value opportunity"
                    : null,
            exit_multiple: lboAssumptions.exit_multiple > lboAssumptions.entry_multiple * 1.5
                ? "⚠️ Exit multiple significantly higher than entry - aggressive assumption"
                : null,
            total_debt: (lboAssumptions.senior_debt_multiple + lboAssumptions.mezz_debt_multiple + lboAssumptions.sub_debt_multiple) > 6
                ? "⚠️ Total debt > 6x EBITDA is very aggressive leverage"
                : null,
            revenue_growth: lboAssumptions.revenue_growth > 0.20
                ? "⚠️ Revenue growth above 20% annually is aggressive"
                : lboAssumptions.revenue_growth < 0
                    ? "⚠️ Negative revenue growth - ensure this is intentional"
                    : null,
        },
        ma: {
            offer_premium: maAssumptions.offer_premium > 0.50
                ? "⚠️ Offer premium above 50% is very high"
                : maAssumptions.offer_premium < 0.10
                    ? "💡 Low premium may face target resistance"
                    : null,
            consideration_mix: maAssumptions.percent_stock + maAssumptions.percent_cash !== 1.0
                ? "⚠️ Stock + Cash should equal 100%"
                : null,
            synergies: (maAssumptions.synergies_revenue + maAssumptions.synergies_cost) > 0 &&
                (maAssumptions.synergies_revenue + maAssumptions.synergies_cost) < 100
                ? "💡 Consider if synergy values are in correct units (₹ Cr)"
                : null,
        },
    };

    // Count active warnings
    const lboWarningCount = Object.values(validationWarnings.lbo).filter(w => w).length;
    const maWarningCount = Object.values(validationWarnings.ma).filter(w => w).length;

    // Theme and enhanced features state
    const [theme, setTheme] = useState<"dark" | "light">("dark");
    const [showHistory, setShowHistory] = useState(false);
    const [jobHistory, setJobHistory] = useState<JobHistoryItem[]>([]);
    const [exportFormats, setExportFormats] = useState<ExportFormat[]>([]);
    const [lboTemplates, setLboTemplates] = useState<LBOTemplate[]>([]);

    // Company Comparison state
    const [compareStocks, setCompareStocks] = useState<Stock[]>([]);
    const [compareSearch, setCompareSearch] = useState("");
    const [compareSearchResults, setCompareSearchResults] = useState<Stock[]>([]);
    const [comparisonData, setComparisonData] = useState<any>(null);
    const [isComparing, setIsComparing] = useState(false);


    // Theme toggle
    useEffect(() => {
        document.documentElement.setAttribute("data-theme", theme);
    }, [theme]);

    // Load stocks, sectors, history, export formats, and templates
    useEffect(() => {
        fetchSectors().then((data) => setSectors(data.sectors)).catch(console.error);
        fetchAllStocks().then((data) => setStocks(data.stocks)).catch(console.error);
        getJobHistory().then((data) => setJobHistory(data.jobs)).catch(console.error);
        getExportFormats().then((data) => setExportFormats(data.formats)).catch(console.error);
        fetchLBOTemplates().then((data) => setLboTemplates(data.templates)).catch(console.error);
    }, []);


    // Filter by sector
    useEffect(() => {
        if (selectedSector) {
            fetchAllStocks(selectedSector).then((data) => setStocks(data.stocks)).catch(console.error);
        } else {
            fetchAllStocks().then((data) => setStocks(data.stocks)).catch(console.error);
        }
    }, [selectedSector]);

    // Search stocks
    useEffect(() => {
        if (searchQuery.length >= 2) {
            if (marketFilter === "us") {
                fetch(`${API_BASE}/stocks/us?search=${searchQuery}&limit=20`)
                    .then(res => res.json())
                    .then(data => setSearchResults(data.stocks || []))
                    .catch(console.error);
            } else {
                searchStocks(searchQuery).then((data) => setSearchResults(data.results)).catch(console.error);
            }
        } else {
            setSearchResults([]);
            setUsStocks([]);
        }
    }, [searchQuery, marketFilter]);

    // M&A Search stocks
    useEffect(() => {
        if (maSearchQuery.length >= 2) {
            searchStocks(maSearchQuery).then((data) => setMaSearchResults(data.results)).catch(console.error);
        } else {
            setMaSearchResults([]);
        }
    }, [maSearchQuery]);

    // Compare Search stocks
    useEffect(() => {
        if (compareSearch.length >= 2) {
            searchStocks(compareSearch).then((data) => setCompareSearchResults(data.results)).catch(console.error);
        } else {
            setCompareSearchResults([]);
        }
    }, [compareSearch]);


    const handleExportPDF = async () => {
        const input = document.getElementById('report-container');
        if (!input) {
            alert("No report content found to export.");
            return;
        }

        try {
            const canvas = await html2canvas(input, {
                scale: 2,
                useCORS: true,
                logging: false,
                backgroundColor: '#111827' // dark-900 background
            });
            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF({
                orientation: 'landscape',
                unit: 'mm',
                format: 'a4'
            });

            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

            pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
            pdf.save(`${jobStatus?.company_name || 'Financial_Model'}_Report.pdf`);
        } catch (err) {
            console.error("PDF Export failed", err);
            alert("Failed to export PDF. Please try again.");
        }
    };

    // Generate model
    const handleGenerate = async () => {
        if (activeTab === "stocks" && !selectedStock) return;
        if (activeTab === "excel" && !excelFile) return;
        if (activeTab === "lbo" && !selectedStock) return;
        if (activeTab === "ma" && (!acquirerStock || !targetStock)) return;

        setIsLoading(true);
        setError(null);
        setJobStatus(null);

        try {
            let job_id: string;

            if (activeTab === "stocks" && selectedStock) {
                const result = await generateModel(selectedStock.symbol, forecastYears);
                job_id = result.job_id;
            } else if (activeTab === "excel" && excelFile) {
                const result = await uploadExcelFile(
                    excelFile,
                    excelCompanyName || excelFile.name.replace(/\.xlsx?$/, ''),
                    excelIndustry,
                    forecastYears
                );
                job_id = result.job_id;
            } else if (activeTab === "lbo" && selectedStock) {
                const result = await generateLBOModel({
                    symbol: selectedStock.symbol,
                    exchange: "NSE",
                    ...lboAssumptions,
                });
                job_id = result.job_id;
            } else if (activeTab === "ma" && acquirerStock && targetStock) {
                const result = await generateMAModel({
                    acquirer_symbol: acquirerStock.symbol,
                    target_symbol: targetStock.symbol,
                    exchange: "NSE",
                    ...maAssumptions,
                });
                job_id = result.job_id;
            } else {
                return;
            }

            setJobStatus({ job_id, status: "pending", progress: 0, message: "Starting..." });
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : "Failed to start model generation. Please try again.";
            setError(errorMessage);
            setIsLoading(false);
        }
    };

    // Compare companies
    const handleCompare = async () => {
        if (compareStocks.length < 2) {
            setError("Select at least 2 companies to compare");
            return;
        }

        setIsComparing(true);
        setError(null);

        try {
            const response = await fetch(`${API_BASE}/api/compare`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    symbols: compareStocks.map(s => s.symbol),
                    exchange: "NSE"
                }),
            });

            if (!response.ok) throw new Error("Comparison failed");

            const data = await response.json();
            setComparisonData(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Comparison failed");
        } finally {
            setIsComparing(false);
        }
    };


    // Poll job status
    useEffect(() => {
        if (!jobStatus || jobStatus.status === "completed" || jobStatus.status === "failed") {
            setIsLoading(false);
            return;
        }

        const interval = setInterval(async () => {
            try {
                const status = await getJobStatus(jobStatus.job_id);
                setJobStatus(status);

                if (status.status === "completed" || status.status === "failed") {
                    setIsLoading(false);
                    clearInterval(interval);
                }
            } catch (err) {
                console.error("Failed to get job status:", err);
            }
        }, 1000);

        return () => clearInterval(interval);
    }, [jobStatus?.job_id, jobStatus?.status]);

    const displayedStocks = searchQuery.length >= 2 ? searchResults : stocks;

    return (
        <main className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-8 relative"
                >
                    {/* Theme and History Controls */}
                    <div className="absolute right-0 top-0 flex items-center gap-2">
                        <button
                            onClick={() => setShowSaveModal(true)}
                            className="p-2.5 rounded-xl bg-primary-500/20 text-primary-400 border border-primary-500/30 hover:bg-primary-500/30 transition-all"
                            title="Save Project"
                        >
                            <Save className="w-5 h-5" />
                        </button>
                        <button
                            onClick={loadProjects}
                            className="p-2.5 rounded-xl bg-blue-500/20 text-blue-400 border border-blue-500/30 hover:bg-blue-500/30 transition-all"
                            title="Open Project"
                        >
                            <FolderOpen className="w-5 h-5" />
                        </button>
                        <button
                            onClick={() => setShowHistory(!showHistory)}
                            className="p-2.5 rounded-xl bg-dark-800/50 border border-dark-600 hover:bg-dark-700 hover:border-dark-500 transition-all"
                            title="View History"
                        >
                            <History className="w-5 h-5 text-dark-300" />
                        </button>
                        <button
                            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                            className="p-2.5 rounded-xl bg-dark-800/50 border border-dark-600 hover:bg-dark-700 hover:border-dark-500 transition-all"
                            title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
                        >
                            {theme === "dark" ? (
                                <Sun className="w-5 h-5 text-yellow-400" />
                            ) : (
                                <Moon className="w-5 h-5 text-dark-300" />
                            )}
                        </button>
                    </div>

                    <div className="flex items-center justify-center gap-3 mb-4">
                        <div className="p-3 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-600 shadow-glow-md">
                            <BarChart3 className="w-8 h-8 text-white" />
                        </div>
                        <h1 className="text-4xl sm:text-5xl font-bold bg-gradient-to-r from-white via-primary-200 to-purple-200 bg-clip-text text-transparent">
                            AI Financial Modeler
                        </h1>
                    </div>
                    <p className="text-dark-300 text-lg max-w-2xl mx-auto">
                        Generate institutional-grade Excel models with{" "}
                        <span className="text-primary-400">DCF, charts, sensitivity analysis</span>
                        {" "}for 150+ Indian stocks
                    </p>
                </motion.div>

                {/* History Sidebar */}
                <AnimatePresence>
                    {showHistory && (
                        <motion.div
                            initial={{ opacity: 0, x: 300 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 300 }}
                            className="fixed right-0 top-0 h-full w-80 bg-dark-900/95 backdrop-blur-lg border-l border-dark-700 z-50 p-6 overflow-y-auto"
                        >
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="text-lg font-semibold text-white">Model History</h3>
                                <button
                                    onClick={() => setShowHistory(false)}
                                    className="p-1.5 rounded-lg hover:bg-dark-800 transition-colors"
                                >
                                    <X className="w-5 h-5 text-dark-400" />
                                </button>
                            </div>

                            {jobHistory.length === 0 ? (
                                <p className="text-dark-400 text-sm">No models generated yet</p>
                            ) : (
                                <div className="space-y-3">
                                    {jobHistory.map((job) => (
                                        <div
                                            key={job.id}
                                            className="p-3 rounded-xl bg-dark-800/50 border border-dark-700 hover:border-dark-600 transition-colors"
                                        >
                                            <p className="font-medium text-white truncate">{job.company_name}</p>
                                            <p className="text-xs text-dark-400 mt-1">
                                                {job.industry || "General"} • {new Date(job.created_at).toLocaleDateString()}
                                            </p>
                                            <div className="flex items-center gap-2 mt-2">
                                                <span className={`px-2 py-0.5 rounded text-xs ${job.status === "completed"
                                                    ? "bg-green-500/20 text-green-400"
                                                    : "bg-yellow-500/20 text-yellow-400"
                                                    }`}>
                                                    {job.status}
                                                </span>
                                                {job.status === "completed" && job.file_path && (
                                                    <a
                                                        href={`/api/download/${job.id}`}
                                                        className="text-xs text-primary-400 hover:underline"
                                                    >
                                                        Download
                                                    </a>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>


                {/* Features Grid */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
                >
                    {FEATURES.map((feature, index) => (
                        <motion.div
                            key={feature.title}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 + index * 0.05 }}
                            className="card p-4 group hover:border-primary-500/30 transition-all duration-300"
                        >
                            <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${feature.color} p-2 mb-3 group-hover:scale-110 transition-transform`}>
                                <feature.icon className="w-full h-full text-white" />
                            </div>
                            <h3 className="font-semibold text-white mb-1">{feature.title}</h3>
                            <p className="text-sm text-dark-400">{feature.description}</p>
                        </motion.div>
                    ))}
                </motion.div>

                {/* Main Content */}
                <div className="grid lg:grid-cols-3 gap-6">
                    {/* Left Panel - Stock Selection */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                        className="lg:col-span-2 card p-6"
                        id="report-container"
                    >
                        {/* Tab Navigation */}
                        <div className="flex gap-2 mb-6 flex-wrap">
                            <button
                                onClick={() => setActiveTab("stocks")}
                                className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${activeTab === "stocks"
                                    ? "bg-primary-500 text-white"
                                    : "bg-dark-700/50 text-dark-300 hover:bg-dark-600"
                                    }`}
                            >
                                <Database className="w-4 h-4" />
                                Select Stock
                            </button>
                            <button
                                onClick={() => setActiveTab("excel")}
                                className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${activeTab === "excel"
                                    ? "bg-primary-500 text-white"
                                    : "bg-dark-700/50 text-dark-300 hover:bg-dark-600"
                                    }`}
                            >
                                <Upload className="w-4 h-4" />
                                Excel Input
                            </button>
                            <button
                                onClick={() => setActiveTab("lbo")}
                                className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${activeTab === "lbo"
                                    ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white"
                                    : "bg-dark-700/50 text-dark-300 hover:bg-dark-600"
                                    }`}
                            >
                                <TrendingUp className="w-4 h-4" />
                                LBO Model
                            </button>
                            <button
                                onClick={() => setActiveTab("ma")}
                                className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${activeTab === "ma"
                                    ? "bg-gradient-to-r from-blue-500 to-green-500 text-white"
                                    : "bg-dark-700/50 text-dark-300 hover:bg-dark-600"
                                    }`}
                            >
                                <Building2 className="w-4 h-4" />
                                M&A Model
                            </button>
                            <button
                                onClick={() => setActiveTab("compare")}
                                className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${activeTab === "compare"
                                    ? "bg-gradient-to-r from-amber-500 to-orange-500 text-white"
                                    : "bg-dark-700/50 text-dark-300 hover:bg-dark-600"
                                    }`}
                            >
                                <BarChart3 className="w-4 h-4" />
                                Compare
                            </button>
                        </div>

                        {activeTab === "stocks" ? (
                            <>
                                {/* Search & Filter */}
                                <div className="flex flex-wrap gap-3 mb-4">
                                    {/* Market Toggle */}
                                    <div className="flex bg-dark-700/50 rounded-lg p-1 border border-dark-600">
                                        <button
                                            onClick={() => setMarketFilter("all")}
                                            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${marketFilter === "all" || marketFilter === "india"
                                                ? "bg-dark-600 text-white shadow-sm"
                                                : "text-dark-400 hover:text-dark-200"
                                                }`}
                                        >
                                            IND
                                        </button>
                                        <button
                                            onClick={() => setMarketFilter("us")}
                                            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${marketFilter === "us"
                                                ? "bg-blue-600 text-white shadow-sm"
                                                : "text-dark-400 hover:text-dark-200"
                                                }`}
                                        >
                                            USA
                                        </button>
                                    </div>

                                    <div className="relative flex-1 min-w-[200px]">
                                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
                                        <input
                                            type="text"
                                            value={searchQuery}
                                            onChange={(e) => setSearchQuery(e.target.value.toUpperCase())}
                                            placeholder={marketFilter === "us" ? "Search US stocks (AAPL, TSLA...)" : "Search filtered stocks..."}
                                            className="input-field w-full pl-12"
                                        />
                                    </div>
                                    <div className="relative">
                                        <select
                                            value={selectedSector}
                                            onChange={(e) => setSelectedSector(e.target.value)}
                                            className="input-field pr-10 appearance-none"
                                        >
                                            <option value="">All Sectors</option>
                                            {sectors.map((sector) => (
                                                <option key={sector} value={sector}>
                                                    {sector.replace("_", " ").toUpperCase()}
                                                </option>
                                            ))}
                                        </select>
                                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400 pointer-events-none" />
                                    </div>
                                </div>

                                {/* Stocks Grid */}
                                <div className="max-h-[400px] overflow-y-auto custom-scrollbar">
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                        {displayedStocks.map((stock) => (
                                            <button
                                                key={stock.symbol}
                                                onClick={() => {
                                                    setSelectedStock(stock);
                                                    setJobStatus(null);
                                                    setError(null);
                                                }}
                                                className={`p-3 rounded-xl border text-left transition-all ${selectedStock?.symbol === stock.symbol
                                                    ? "border-primary-500 bg-primary-500/10"
                                                    : "border-dark-600 hover:border-dark-500 bg-dark-800/50"
                                                    }`}
                                            >
                                                <div className="flex items-center justify-between">
                                                    <div>
                                                        <p className="font-semibold text-white">{stock.symbol}</p>
                                                        <p className="text-sm text-dark-400 truncate max-w-[180px]">{stock.name}</p>
                                                    </div>
                                                    <span className={`text-xs px-2 py-1 rounded-lg border ${SECTOR_COLORS[stock.sector_code || ""] || "bg-dark-600/50 text-dark-300 border-dark-500"
                                                        }`}>
                                                        {stock.sector_code?.replace("_", " ")}
                                                    </span>
                                                </div>
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </>
                        ) : activeTab === "excel" ? (
                            /* Excel File Upload */
                            <div className="space-y-4">
                                {/* File Drop Zone */}
                                <div
                                    className={`relative p-8 rounded-xl border-2 border-dashed transition-all cursor-pointer ${isDragging
                                        ? "border-primary-500 bg-primary-500/10"
                                        : excelFile
                                            ? "border-green-500 bg-green-500/10"
                                            : "border-dark-600 hover:border-dark-500 bg-dark-800/50"
                                        }`}
                                    onDragOver={(e) => {
                                        e.preventDefault();
                                        setIsDragging(true);
                                    }}
                                    onDragLeave={(e) => {
                                        e.preventDefault();
                                        setIsDragging(false);
                                    }}
                                    onDrop={(e) => {
                                        e.preventDefault();
                                        setIsDragging(false);
                                        const files = e.dataTransfer.files;
                                        if (files.length > 0 && files[0].name.match(/\.xlsx?$/i)) {
                                            setExcelFile(files[0]);
                                        }
                                    }}
                                    onClick={() => document.getElementById('excel-file-input')?.click()}
                                >
                                    <input
                                        id="excel-file-input"
                                        type="file"
                                        accept=".xlsx,.xls"
                                        className="hidden"
                                        onChange={(e) => {
                                            const files = e.target.files;
                                            if (files && files.length > 0) {
                                                setExcelFile(files[0]);
                                            }
                                        }}
                                    />
                                    <div className="text-center">
                                        {excelFile ? (
                                            <>
                                                <div className="w-16 h-16 mx-auto mb-3 rounded-2xl bg-green-500/20 flex items-center justify-center">
                                                    <FileSpreadsheet className="w-8 h-8 text-green-400" />
                                                </div>
                                                <p className="font-semibold text-white mb-1">{excelFile.name}</p>
                                                <p className="text-sm text-dark-400">
                                                    {(excelFile.size / 1024).toFixed(1)} KB
                                                </p>
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setExcelFile(null);
                                                    }}
                                                    className="mt-3 text-sm text-red-400 hover:text-red-300 flex items-center gap-1 mx-auto"
                                                >
                                                    <X className="w-4 h-4" />
                                                    Remove file
                                                </button>
                                            </>
                                        ) : (
                                            <>
                                                <div className="w-16 h-16 mx-auto mb-3 rounded-2xl bg-dark-700/50 flex items-center justify-center">
                                                    <Upload className="w-8 h-8 text-dark-400" />
                                                </div>
                                                <p className="font-semibold text-white mb-1">Drop Excel file here</p>
                                                <p className="text-sm text-dark-400">or click to browse</p>
                                                <p className="text-xs text-dark-500 mt-2">Supports .xlsx and .xls files</p>
                                            </>
                                        )}
                                    </div>
                                </div>

                                {/* Company Name & Industry */}
                                <div className="grid md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-dark-300 mb-2">
                                            Company Name (optional)
                                        </label>
                                        <input
                                            type="text"
                                            value={excelCompanyName}
                                            onChange={(e) => setExcelCompanyName(e.target.value)}
                                            placeholder="Extracted from file if empty"
                                            className="input-field w-full"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-dark-300 mb-2">
                                            Industry
                                        </label>
                                        <select
                                            value={excelIndustry}
                                            onChange={(e) => setExcelIndustry(e.target.value)}
                                            className="input-field w-full"
                                        >
                                            <option value="general">General Corporate</option>
                                            <option value="power">Power & Utilities</option>
                                            <option value="banking">Banking</option>
                                            <option value="it">IT Services</option>
                                            <option value="pharma">Pharmaceuticals</option>
                                            <option value="fmcg">FMCG</option>
                                            <option value="auto">Automobiles</option>
                                            <option value="metals">Metals & Mining</option>
                                            <option value="oil_gas">Oil & Gas</option>
                                            <option value="cement">Cement</option>
                                            <option value="infra">Infrastructure</option>
                                        </select>
                                    </div>
                                </div>

                                {/* Expected Format Info */}
                                <div className="p-4 rounded-xl bg-dark-800/50 border border-dark-600">
                                    <h4 className="font-medium text-white mb-2 flex items-center gap-2">
                                        <FileSpreadsheet className="w-4 h-4 text-primary-400" />
                                        Supported Excel Formats
                                    </h4>
                                    <ul className="text-sm text-dark-400 space-y-1">
                                        <li>• Rows labeled: Revenue, EBITDA, Net Income, etc.</li>
                                        <li>• Multiple sheets: Income Statement, Balance Sheet</li>
                                        <li>• Screener.in or similar export formats</li>
                                        <li>• Company name auto-detected from header</li>
                                    </ul>
                                </div>
                            </div>
                        ) : activeTab === "lbo" ? (
                            /* LBO Model Configuration */
                            <div className="space-y-4">
                                {/* Stock Selection for LBO */}
                                <div>
                                    <label className="block text-sm font-medium text-dark-300 mb-2">
                                        Select Target Company
                                    </label>
                                    <div className="relative">
                                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
                                        <input
                                            type="text"
                                            value={searchQuery}
                                            onChange={(e) => setSearchQuery(e.target.value.toUpperCase())}
                                            placeholder="Search stocks..."
                                            className="input-field w-full pl-12"
                                        />
                                    </div>
                                    {searchResults.length > 0 && (
                                        <div className="mt-2 max-h-32 overflow-y-auto border border-dark-600 rounded-lg">
                                            {searchResults.slice(0, 5).map((stock) => (
                                                <button
                                                    key={stock.symbol}
                                                    onClick={() => {
                                                        setSelectedStock(stock);
                                                        setSearchQuery("");
                                                        setSearchResults([]);
                                                    }}
                                                    className="w-full p-2 text-left hover:bg-dark-700 text-sm"
                                                >
                                                    <span className="font-semibold text-white">{stock.symbol}</span>
                                                    <span className="text-dark-400 ml-2">{stock.name}</span>
                                                </button>
                                            ))}
                                        </div>
                                    )}
                                    {selectedStock && (
                                        <div className="mt-2 p-2 rounded-lg bg-primary-500/10 border border-primary-500/30 flex items-center justify-between">
                                            <span className="text-white font-medium">{selectedStock.symbol} - {selectedStock.name}</span>
                                            <button onClick={() => setSelectedStock(null)} className="text-dark-400 hover:text-white">
                                                <X className="w-4 h-4" />
                                            </button>
                                        </div>
                                    )}
                                </div>

                                {/* Transaction Assumptions */}
                                <div className="p-4 rounded-xl bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20">
                                    <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                                        <DollarSign className="w-4 h-4 text-purple-400" />
                                        Transaction Assumptions
                                    </h4>
                                    <div className="grid md:grid-cols-3 gap-3">
                                        <div>
                                            <label className="block text-xs text-dark-400 mb-1">Hold Period (Yrs)</label>
                                            <input
                                                type="number"
                                                value={lboAssumptions.holding_period}
                                                onChange={(e) => setLboAssumptions({ ...lboAssumptions, holding_period: parseInt(e.target.value) || 5 })}
                                                className="input-field w-full text-sm"
                                                min={3} max={10}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-xs text-dark-400 mb-1">Entry Multiple (x)</label>
                                            <input
                                                type="number"
                                                step="0.5"
                                                value={lboAssumptions.entry_multiple}
                                                onChange={(e) => setLboAssumptions({ ...lboAssumptions, entry_multiple: parseFloat(e.target.value) || 8 })}
                                                className="input-field w-full text-sm"
                                                min={3} max={20}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-xs text-dark-400 mb-1">Exit Multiple (x)</label>
                                            <input
                                                type="number"
                                                step="0.5"
                                                value={lboAssumptions.exit_multiple}
                                                onChange={(e) => setLboAssumptions({ ...lboAssumptions, exit_multiple: parseFloat(e.target.value) || 8 })}
                                                className="input-field w-full text-sm"
                                                min={3} max={20}
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Debt Structure */}
                                <div className="p-4 rounded-xl bg-dark-800/50 border border-dark-600">
                                    <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                                        <BarChart3 className="w-4 h-4 text-blue-400" />
                                        Debt Structure
                                    </h4>
                                    <div className="space-y-3">
                                        {/* Senior Debt */}
                                        <div className="grid grid-cols-2 gap-2">
                                            <div>
                                                <label className="block text-xs text-blue-400 mb-1">Senior Debt (x EBITDA)</label>
                                                <input
                                                    type="number"
                                                    step="0.5"
                                                    value={lboAssumptions.senior_debt_multiple}
                                                    onChange={(e) => setLboAssumptions({ ...lboAssumptions, senior_debt_multiple: parseFloat(e.target.value) || 3 })}
                                                    className="input-field w-full text-sm"
                                                    min={0} max={6}
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-xs text-blue-400 mb-1">Senior Rate (%)</label>
                                                <input
                                                    type="number"
                                                    step="0.5"
                                                    value={(lboAssumptions.senior_interest_rate * 100).toFixed(1)}
                                                    onChange={(e) => setLboAssumptions({ ...lboAssumptions, senior_interest_rate: (parseFloat(e.target.value) || 8) / 100 })}
                                                    className="input-field w-full text-sm"
                                                    min={3} max={20}
                                                />
                                            </div>
                                        </div>
                                        {/* Mezz Debt */}
                                        <div className="grid grid-cols-2 gap-2">
                                            <div>
                                                <label className="block text-xs text-purple-400 mb-1">Mezz Debt (x EBITDA)</label>
                                                <input
                                                    type="number"
                                                    step="0.5"
                                                    value={lboAssumptions.mezz_debt_multiple}
                                                    onChange={(e) => setLboAssumptions({ ...lboAssumptions, mezz_debt_multiple: parseFloat(e.target.value) || 1.5 })}
                                                    className="input-field w-full text-sm"
                                                    min={0} max={3}
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-xs text-purple-400 mb-1">Mezz Rate (%)</label>
                                                <input
                                                    type="number"
                                                    step="0.5"
                                                    value={(lboAssumptions.mezz_interest_rate * 100).toFixed(1)}
                                                    onChange={(e) => setLboAssumptions({ ...lboAssumptions, mezz_interest_rate: (parseFloat(e.target.value) || 12) / 100 })}
                                                    className="input-field w-full text-sm"
                                                    min={5} max={25}
                                                />
                                            </div>
                                        </div>
                                        {/* Sub Debt */}
                                        <div className="grid grid-cols-2 gap-2">
                                            <div>
                                                <label className="block text-xs text-red-400 mb-1">Sub Debt (x EBITDA)</label>
                                                <input
                                                    type="number"
                                                    step="0.5"
                                                    value={lboAssumptions.sub_debt_multiple}
                                                    onChange={(e) => setLboAssumptions({ ...lboAssumptions, sub_debt_multiple: parseFloat(e.target.value) || 0.5 })}
                                                    className="input-field w-full text-sm"
                                                    min={0} max={2}
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-xs text-red-400 mb-1">Sub Rate (%)</label>
                                                <input
                                                    type="number"
                                                    step="0.5"
                                                    value={(lboAssumptions.sub_interest_rate * 100).toFixed(1)}
                                                    onChange={(e) => setLboAssumptions({ ...lboAssumptions, sub_interest_rate: (parseFloat(e.target.value) || 14) / 100 })}
                                                    className="input-field w-full text-sm"
                                                    min={5} max={25}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Operating Assumptions */}
                                <div className="p-4 rounded-xl bg-dark-800/50 border border-dark-600">
                                    <div className="flex justify-between items-center mb-3">
                                        <h4 className="font-medium text-white flex items-center gap-2">
                                            <LineChart className="w-4 h-4 text-green-400" />
                                            Operating Assumptions
                                        </h4>
                                        <select
                                            className="bg-dark-700 text-xs px-2 py-1 rounded border border-dark-600 text-dark-300 focus:outline-none focus:border-primary-500"
                                            onChange={(e) => {
                                                const t = lboTemplates.find(t => t.id === e.target.value);
                                                if (t) {
                                                    setLboAssumptions(prev => ({
                                                        ...prev,
                                                        revenue_growth: t.assumptions.revenue_growth || prev.revenue_growth,
                                                        ebitda_margin: t.assumptions.ebitda_margin || prev.ebitda_margin,
                                                        // Map other fields if needed, or use spread if keys match exactly
                                                    }));
                                                }
                                            }}
                                        >
                                            <option value="">Load Template...</option>
                                            {lboTemplates.map(t => (
                                                <option key={t.id} value={t.id}>{t.name}</option>
                                            ))}
                                        </select>
                                    </div>
                                    <div className="grid md:grid-cols-2 gap-3">
                                        <div>
                                            <label className="block text-xs text-dark-400 mb-1">Revenue Growth (%)</label>
                                            <input
                                                type="number"
                                                step="1"
                                                value={(lboAssumptions.revenue_growth * 100).toFixed(0)}
                                                onChange={(e) => setLboAssumptions({ ...lboAssumptions, revenue_growth: (parseFloat(e.target.value) || 8) / 100 })}
                                                className="input-field w-full text-sm"
                                                min={-20} max={50}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-xs text-dark-400 mb-1">EBITDA Margin (%)</label>
                                            <input
                                                type="number"
                                                step="1"
                                                value={(lboAssumptions.ebitda_margin * 100).toFixed(0)}
                                                onChange={(e) => setLboAssumptions({ ...lboAssumptions, ebitda_margin: (parseFloat(e.target.value) || 25) / 100 })}
                                                className="input-field w-full text-sm"
                                                min={5} max={60}
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* LBO Model Info */}
                                <div className="p-4 rounded-xl bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/30">
                                    <h4 className="font-medium text-white mb-2">LBO Model Includes:</h4>
                                    <ul className="text-sm text-dark-300 space-y-1">
                                        <li>• Sources & Uses of Funds</li>
                                        <li>• Debt Schedules (Senior, Mezz, Sub)</li>
                                        <li>• Operating Model & Cash Flow</li>
                                        <li>• Returns Analysis (IRR, MoIC)</li>
                                        <li>• Sensitivity Tables</li>
                                    </ul>
                                </div>

                                {/* LBO Validation Warnings */}
                                {lboWarningCount > 0 && (
                                    <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30">
                                        <h4 className="font-medium text-amber-400 mb-2 flex items-center gap-2">
                                            <AlertCircle className="w-4 h-4" />
                                            Assumption Warnings ({lboWarningCount})
                                        </h4>
                                        <ul className="text-sm text-amber-200 space-y-1">
                                            {validationWarnings.lbo.ebitda_margin && (
                                                <li className="flex items-start gap-2">
                                                    <span className="text-xs">{validationWarnings.lbo.ebitda_margin}</span>
                                                </li>
                                            )}
                                            {validationWarnings.lbo.entry_multiple && (
                                                <li className="flex items-start gap-2">
                                                    <span className="text-xs">{validationWarnings.lbo.entry_multiple}</span>
                                                </li>
                                            )}
                                            {validationWarnings.lbo.exit_multiple && (
                                                <li className="flex items-start gap-2">
                                                    <span className="text-xs">{validationWarnings.lbo.exit_multiple}</span>
                                                </li>
                                            )}
                                            {validationWarnings.lbo.total_debt && (
                                                <li className="flex items-start gap-2">
                                                    <span className="text-xs">{validationWarnings.lbo.total_debt}</span>
                                                </li>
                                            )}
                                            {validationWarnings.lbo.revenue_growth && (
                                                <li className="flex items-start gap-2">
                                                    <span className="text-xs">{validationWarnings.lbo.revenue_growth}</span>
                                                </li>
                                            )}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        ) : activeTab === "ma" ? (
                            /* M&A Model Configuration */
                            <div className="space-y-4">
                                {/* Acquirer Selection */}
                                <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20">
                                    <h4 className="font-medium text-blue-400 mb-3 flex items-center gap-2">
                                        <Building2 className="w-4 h-4" />
                                        Acquirer Company
                                    </h4>
                                    <div className="relative">
                                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400" />
                                        <input
                                            type="text"
                                            value={maSearchType === "acquirer" ? maSearchQuery : ""}
                                            onChange={(e) => {
                                                setMaSearchType("acquirer");
                                                setMaSearchQuery(e.target.value.toUpperCase());
                                            }}
                                            onFocus={() => setMaSearchType("acquirer")}
                                            placeholder="Search acquirer..."
                                            className="input-field w-full pl-10 text-sm"
                                        />
                                    </div>
                                    {maSearchType === "acquirer" && maSearchResults.length > 0 && (
                                        <div className="mt-2 max-h-24 overflow-y-auto border border-dark-600 rounded-lg">
                                            {maSearchResults.slice(0, 4).map((stock) => (
                                                <button
                                                    key={stock.symbol}
                                                    onClick={() => {
                                                        setAcquirerStock(stock);
                                                        setMaSearchQuery("");
                                                        setMaSearchResults([]);
                                                    }}
                                                    className="w-full p-2 text-left hover:bg-dark-700 text-xs"
                                                >
                                                    <span className="font-semibold text-white">{stock.symbol}</span>
                                                    <span className="text-dark-400 ml-2">{stock.name}</span>
                                                </button>
                                            ))}
                                        </div>
                                    )}
                                    {acquirerStock && (
                                        <div className="mt-2 p-2 rounded-lg bg-blue-500/20 border border-blue-500/30 flex items-center justify-between">
                                            <span className="text-white text-sm font-medium">{acquirerStock.symbol}</span>
                                            <button onClick={() => setAcquirerStock(null)} className="text-dark-400 hover:text-white">
                                                <X className="w-4 h-4" />
                                            </button>
                                        </div>
                                    )}
                                </div>

                                {/* Target Selection */}
                                <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/20">
                                    <h4 className="font-medium text-green-400 mb-3 flex items-center gap-2">
                                        <TrendingUp className="w-4 h-4" />
                                        Target Company
                                    </h4>
                                    <div className="relative">
                                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400" />
                                        <input
                                            type="text"
                                            value={maSearchType === "target" ? maSearchQuery : ""}
                                            onChange={(e) => {
                                                setMaSearchType("target");
                                                setMaSearchQuery(e.target.value.toUpperCase());
                                            }}
                                            onFocus={() => setMaSearchType("target")}
                                            placeholder="Search target..."
                                            className="input-field w-full pl-10 text-sm"
                                        />
                                    </div>
                                    {maSearchType === "target" && maSearchResults.length > 0 && (
                                        <div className="mt-2 max-h-24 overflow-y-auto border border-dark-600 rounded-lg">
                                            {maSearchResults.slice(0, 4).map((stock) => (
                                                <button
                                                    key={stock.symbol}
                                                    onClick={() => {
                                                        setTargetStock(stock);
                                                        setMaSearchQuery("");
                                                        setMaSearchResults([]);
                                                    }}
                                                    className="w-full p-2 text-left hover:bg-dark-700 text-xs"
                                                >
                                                    <span className="font-semibold text-white">{stock.symbol}</span>
                                                    <span className="text-dark-400 ml-2">{stock.name}</span>
                                                </button>
                                            ))}
                                        </div>
                                    )}
                                    {targetStock && (
                                        <div className="mt-2 p-2 rounded-lg bg-green-500/20 border border-green-500/30 flex items-center justify-between">
                                            <span className="text-white text-sm font-medium">{targetStock.symbol}</span>
                                            <button onClick={() => setTargetStock(null)} className="text-dark-400 hover:text-white">
                                                <X className="w-4 h-4" />
                                            </button>
                                        </div>
                                    )}
                                </div>

                                {/* Transaction Terms */}
                                <div className="p-4 rounded-xl bg-dark-800/50 border border-dark-600">
                                    <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                                        <DollarSign className="w-4 h-4 text-purple-400" />
                                        Transaction Terms
                                    </h4>
                                    <div className="grid grid-cols-3 gap-3">
                                        <div>
                                            <label className="block text-xs text-dark-400 mb-1">Offer Premium (%)</label>
                                            <input
                                                type="number"
                                                step="5"
                                                value={(maAssumptions.offer_premium * 100).toFixed(0)}
                                                onChange={(e) => setMaAssumptions({ ...maAssumptions, offer_premium: (parseFloat(e.target.value) || 25) / 100 })}
                                                className="input-field w-full text-sm"
                                                min={0} max={100}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-xs text-dark-400 mb-1">Stock (%)</label>
                                            <input
                                                type="number"
                                                step="10"
                                                value={(maAssumptions.percent_stock * 100).toFixed(0)}
                                                onChange={(e) => {
                                                    const stock = (parseFloat(e.target.value) || 50) / 100;
                                                    setMaAssumptions({ ...maAssumptions, percent_stock: stock, percent_cash: 1 - stock });
                                                }}
                                                className="input-field w-full text-sm"
                                                min={0} max={100}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-xs text-dark-400 mb-1">Cash (%)</label>
                                            <input
                                                type="number"
                                                value={(maAssumptions.percent_cash * 100).toFixed(0)}
                                                className="input-field w-full text-sm bg-dark-700"
                                                disabled
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Synergies */}
                                <div className="p-4 rounded-xl bg-dark-800/50 border border-dark-600">
                                    <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                                        <Sparkles className="w-4 h-4 text-yellow-400" />
                                        Synergies (₹ Crores)
                                    </h4>
                                    <div className="grid grid-cols-2 gap-3">
                                        <div>
                                            <label className="block text-xs text-dark-400 mb-1">Revenue Synergies</label>
                                            <input
                                                type="number"
                                                value={maAssumptions.synergies_revenue}
                                                onChange={(e) => setMaAssumptions({ ...maAssumptions, synergies_revenue: parseFloat(e.target.value) || 0 })}
                                                className="input-field w-full text-sm"
                                                min={0}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-xs text-dark-400 mb-1">Cost Synergies</label>
                                            <input
                                                type="number"
                                                value={maAssumptions.synergies_cost}
                                                onChange={(e) => setMaAssumptions({ ...maAssumptions, synergies_cost: parseFloat(e.target.value) || 0 })}
                                                className="input-field w-full text-sm"
                                                min={0}
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* M&A Model Info */}
                                <div className="p-4 rounded-xl bg-gradient-to-r from-blue-500/10 to-green-500/10 border border-blue-500/30">
                                    <h4 className="font-medium text-white mb-2">M&A Model Includes:</h4>
                                    <ul className="text-sm text-dark-300 space-y-1">
                                        <li>• Accretion / Dilution Analysis</li>
                                        <li>• Pro Forma Combined Financials</li>
                                        <li>• Synergy Phase-in Schedule</li>
                                        <li>• Sources & Uses</li>
                                        <li>• Sensitivity Tables</li>
                                    </ul>
                                </div>
                            </div>
                        ) : activeTab === "compare" ? (
                            /* Company Comparison */
                            <div className="space-y-4">
                                <div className="p-4 rounded-xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20">
                                    <h3 className="font-medium text-white mb-3">Select Companies to Compare</h3>

                                    {/* Search */}
                                    <div className="relative mb-3">
                                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
                                        <input
                                            type="text"
                                            value={compareSearch}
                                            onChange={(e) => setCompareSearch(e.target.value.toUpperCase())}
                                            placeholder="Search stocks to add..."
                                            className="input-field w-full pl-12"
                                        />
                                    </div>

                                    {/* Search Results */}
                                    {compareSearchResults.length > 0 && (
                                        <div className="max-h-40 overflow-y-auto custom-scrollbar mb-3">
                                            <div className="space-y-1">
                                                {compareSearchResults.map((stock) => (
                                                    <button
                                                        key={stock.symbol}
                                                        onClick={() => {
                                                            if (!compareStocks.find(s => s.symbol === stock.symbol) && compareStocks.length < 5) {
                                                                setCompareStocks([...compareStocks, stock]);
                                                                setCompareSearch("");
                                                                setCompareSearchResults([]);
                                                            }
                                                        }}
                                                        className="w-full p-2 rounded-lg border border-dark-600 hover:border-primary-500 bg-dark-800/50 text-left transition-all"
                                                        disabled={compareStocks.find(s => s.symbol === stock.symbol) !== undefined || compareStocks.length >= 5}
                                                    >
                                                        <p className="font-medium text-white text-sm">{stock.symbol}</p>
                                                        <p className="text-xs text-dark-400">{stock.name}</p>
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Selected Stocks */}
                                    {compareStocks.length > 0 && (
                                        <div>
                                            <h4 className="text-sm font-medium text-dark-300 mb-2">Selected ({compareStocks.length}/5)</h4>
                                            <div className="flex flex-wrap gap-2">
                                                {compareStocks.map((stock) => (
                                                    <div
                                                        key={stock.symbol}
                                                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary-500/20 border border-primary-500/30"
                                                    >
                                                        <span className="text-sm text-white font-medium">{stock.symbol}</span>
                                                        <button
                                                            onClick={() => setCompareStocks(compareStocks.filter(s => s.symbol !== stock.symbol))}
                                                            className="text-dark-400 hover:text-white"
                                                        >
                                                            <X className="w-3 h-3" />
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Compare Button */}
                                    <button
                                        onClick={handleCompare}
                                        disabled={compareStocks.length < 2 || isComparing}
                                        className="btn-primary w-full mt-3 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2"
                                    >
                                        {isComparing ? (
                                            <>
                                                <Loader2 className="w-5 h-5 animate-spin" />
                                                Comparing...
                                            </>
                                        ) : (
                                            <>
                                                <BarChart3 className="w-5 h-5" />
                                                Compare Companies
                                            </>
                                        )}
                                    </button>
                                </div>

                                {/* Comparison Results */}
                                {comparisonData && (
                                    <div className="p-4 rounded-xl bg-dark-800/50 border border-dark-600">
                                        <h3 className="font-medium text-white mb-3">Comparison Results</h3>
                                        <div className="overflow-x-auto">
                                            <table className="w-full text-sm">
                                                <thead>
                                                    <tr className="border-b border-dark-600">
                                                        <th className="text-left py-2 px-3 text-dark-300 font-medium">Metric</th>
                                                        {comparisonData.companies.map((company: any) => (
                                                            <th key={company.symbol} className="text-right py-2 px-3 text-white font-medium">
                                                                {company.symbol}
                                                            </th>
                                                        ))}
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr className="border-b border-dark-700">
                                                        <td className="py-2 px-3 text-dark-400">Market Cap (Cr)</td>
                                                        {comparisonData.companies.map((company: any) => (
                                                            <td key={company.symbol} className="text-right py-2 px-3 text-white">
                                                                {company.market_cap ? company.market_cap.toFixed(0) : "N/A"}
                                                            </td>
                                                        ))}
                                                    </tr>
                                                    <tr className="border-b border-dark-700">
                                                        <td className="py-2 px-3 text-dark-400">P/E Ratio</td>
                                                        {comparisonData.companies.map((company: any) => (
                                                            <td key={company.symbol} className="text-right py-2 px-3 text-white">
                                                                {company.pe_ratio ? company.pe_ratio.toFixed(1) : "N/A"}
                                                            </td>
                                                        ))}
                                                    </tr>
                                                    <tr className="border-b border-dark-700">
                                                        <td className="py-2 px-3 text-dark-400">EBITDA Margin (%)</td>
                                                        {comparisonData.companies.map((company: any) => (
                                                            <td key={company.symbol} className="text-right py-2 px-3 text-white">
                                                                {company.ebitda_margin ? (company.ebitda_margin * 100).toFixed(1) + "%" : "N/A"}
                                                            </td>
                                                        ))}
                                                    </tr>
                                                    <tr className="border-b border-dark-700">
                                                        <td className="py-2 px-3 text-dark-400">ROE (%)</td>
                                                        {comparisonData.companies.map((company: any) => (
                                                            <td key={company.symbol} className="text-right py-2 px-3 text-white">
                                                                {company.roe ? (company.roe * 100).toFixed(1) + "%" : "N/A"}
                                                            </td>
                                                        ))}
                                                    </tr>
                                                    <tr>
                                                        <td className="py-2 px-3 text-dark-400">Debt/Equity</td>
                                                        {comparisonData.companies.map((company: any) => (
                                                            <td key={company.symbol} className="text-right py-2 px-3 text-white">
                                                                {company.debt_to_equity ? company.debt_to_equity.toFixed(2) : "N/A"}
                                                            </td>
                                                        ))}
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : null}

                        {/* Error Display */}
                        <AnimatePresence>
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: "auto" }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="mt-4"
                                >
                                    <div className="flex items-center gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400">
                                        <AlertCircle className="w-5 h-5 flex-shrink-0" />
                                        <p>{error}</p>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </motion.div>

                    {/* Right Panel - Configuration & Progress */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 }}
                        className="card p-6"
                    >
                        {/* Selected Stock / Company Info */}
                        {(selectedStock || (activeTab === "excel" && excelFile) || (activeTab === "ma" && (acquirerStock || targetStock))) && (
                            <div className="mb-6">
                                <div className="p-4 rounded-xl bg-gradient-to-r from-primary-500/10 to-purple-500/10 border border-primary-500/20">
                                    <div className="flex items-center gap-2 mb-1">
                                        <Building2 className="w-5 h-5 text-primary-400" />
                                        <h3 className="font-semibold text-white">
                                            {activeTab === "stocks" || activeTab === "lbo"
                                                ? selectedStock?.name
                                                : activeTab === "ma"
                                                    ? `${acquirerStock?.symbol || "?"} + ${targetStock?.symbol || "?"}`
                                                    : (excelCompanyName || excelFile?.name || "Uploaded File")
                                            }
                                        </h3>
                                    </div>
                                    <p className="text-sm text-dark-400">
                                        {activeTab === "stocks"
                                            ? `${selectedStock?.symbol} • ${selectedStock?.sector}`
                                            : activeTab === "lbo"
                                                ? `LBO Model • ${selectedStock?.symbol}`
                                                : activeTab === "ma"
                                                    ? `M&A Model • ${acquirerStock?.name || "Acquirer"} acquiring ${targetStock?.name || "Target"}`
                                                    : `Excel Upload • ${excelIndustry.replace("_", " ")}`
                                        }
                                    </p>
                                </div>
                            </div>
                        )}

                        {/* Configuration */}
                        {!jobStatus && (
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-dark-300 mb-2">
                                        Forecast Period
                                    </label>
                                    <select
                                        value={forecastYears}
                                        onChange={(e) => {
                                            setForecastYears(parseInt(e.target.value));
                                        }}
                                        className="input-field w-full"
                                    >
                                        {[3, 5, 7, 10].map((years) => (
                                            <option key={years} value={years}>
                                                {years} Years
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <button
                                    onClick={handleGenerate}
                                    disabled={
                                        isLoading ||
                                        (activeTab === "stocks" && !selectedStock) ||
                                        (activeTab === "excel" && !excelFile) ||
                                        (activeTab === "lbo" && !selectedStock) ||
                                        (activeTab === "ma" && (!acquirerStock || !targetStock))
                                    }
                                    className="btn-primary w-full flex items-center justify-center gap-2"
                                >
                                    {isLoading ? (
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                    ) : (
                                        <Sparkles className="w-5 h-5" />
                                    )}
                                    Generate Model
                                    <ChevronRight className="w-5 h-5" />
                                </button>

                                {/* Model Features */}
                                <div className="pt-4 border-t border-dark-600">
                                    <h4 className="text-sm font-medium text-dark-300 mb-3">Model Includes:</h4>
                                    <ul className="space-y-2">
                                        {(activeTab === "lbo" ? [
                                            "Sources & Uses of Funds",
                                            "Debt Schedules (Senior, Mezz, Sub)",
                                            "Operating Model & Cash Flow",
                                            "Returns Analysis (IRR, MoIC)",
                                            "Sensitivity Tables",
                                        ] : activeTab === "ma" ? [
                                            "Accretion / Dilution Analysis",
                                            "Pro Forma Combined Financials",
                                            "Synergy Phase-in Schedule",
                                            "Sources & Uses",
                                            "Sensitivity Tables",
                                        ] : [
                                            "Income Statement (5Y Historical + Forecast)",
                                            "Balance Sheet with Balance Check",
                                            "Cash Flow Statement",
                                            "DCF Valuation with WACC",
                                            "Sensitivity Analysis",
                                            "Scenario Analysis (Bear/Base/Bull)",
                                            "Dashboard with Charts",
                                        ]).map((item) => (
                                            <li key={item} className="flex items-center gap-2 text-sm text-dark-400">
                                                <CheckCircle className="w-4 h-4 text-green-400" />
                                                {item}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        )}

                        {/* Progress Display */}
                        <AnimatePresence>
                            {jobStatus && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                >
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                {jobStatus.status === "completed" ? (
                                                    <CheckCircle className="w-6 h-6 text-green-400" />
                                                ) : jobStatus.status === "failed" ? (
                                                    <AlertCircle className="w-6 h-6 text-red-400" />
                                                ) : (
                                                    <Loader2 className="w-6 h-6 text-primary-400 animate-spin" />
                                                )}
                                                <div>
                                                    <p className="font-medium text-white">
                                                        {jobStatus.company_name || selectedStock?.name || excelCompanyName || "Custom Model"}
                                                    </p>
                                                    <p className="text-sm text-dark-400">{jobStatus.industry}</p>
                                                </div>
                                            </div>
                                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${jobStatus.status === "completed"
                                                ? "bg-green-500/20 text-green-400"
                                                : jobStatus.status === "failed"
                                                    ? "bg-red-500/20 text-red-400"
                                                    : "bg-primary-500/20 text-primary-400"
                                                }`}>
                                                {jobStatus.status === "completed" ? "Ready" :
                                                    jobStatus.status === "failed" ? "Failed" :
                                                        `${jobStatus.progress}%`}
                                            </span>
                                        </div>

                                        {/* Progress bar */}
                                        <div className="h-2 bg-dark-600 rounded-full overflow-hidden">
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: `${jobStatus.progress}%` }}
                                                className="h-full progress-bar rounded-full"
                                            />
                                        </div>

                                        <p className="text-sm text-dark-400">{jobStatus.message}</p>

                                        {/* Download button */}
                                        {jobStatus.status === "completed" && jobStatus.download_url && (
                                            <motion.div
                                                initial={{ opacity: 0, y: 10 }}
                                                animate={{ opacity: 1, y: 0 }}
                                            >
                                                <a
                                                    href={jobStatus.download_url}
                                                    download
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="btn-primary w-full inline-flex items-center justify-center gap-2"
                                                    onClick={(e) => {
                                                        e.preventDefault();
                                                        // Programmatic download to ensure file is downloaded
                                                        fetch(jobStatus.download_url!)
                                                            .then(res => res.blob())
                                                            .then(blob => {
                                                                const url = window.URL.createObjectURL(blob);
                                                                const a = document.createElement('a');
                                                                a.href = url;
                                                                a.download = jobStatus.filename || 'financial_model.xlsx';
                                                                document.body.appendChild(a);
                                                                a.click();
                                                                a.remove();
                                                                window.URL.revokeObjectURL(url);
                                                            });
                                                    }}
                                                >
                                                    <Download className="w-5 h-5" />
                                                    Download Excel Model
                                                </a>

                                                {/* PDF Export Button */}
                                                <button
                                                    onClick={handleExportPDF}
                                                    className="btn-secondary w-full mt-2 inline-flex items-center justify-center gap-2"
                                                >
                                                    <FileText className="w-5 h-5" />
                                                    Export to PDF
                                                </button>

                                                {/* PowerPoint Export Button */}
                                                <button
                                                    onClick={async () => {
                                                        try {
                                                            await downloadExportFile(jobStatus.job_id, "pptx");
                                                        } catch (err) {
                                                            alert("PowerPoint export failed. Please try again.");
                                                        }
                                                    }}
                                                    className="btn-secondary w-full mt-2 inline-flex items-center justify-center gap-2"
                                                >
                                                    <Presentation className="w-5 h-5" />
                                                    Export to PowerPoint
                                                </button>

                                                {/* Excel with VBA Export Button */}
                                                <button
                                                    onClick={async () => {
                                                        try {
                                                            await downloadExportFile(jobStatus.job_id, "xlsm");
                                                        } catch (err) {
                                                            alert("Excel with VBA export failed. Please try again.");
                                                        }
                                                    }}
                                                    className="btn-secondary w-full mt-2 inline-flex items-center justify-center gap-2 border-green-500/30 hover:bg-green-500/10"
                                                >
                                                    <Code className="w-5 h-5 text-green-400" />
                                                    Download with VBA Macros
                                                </button>

                                                {/* Monte Carlo Simulation Section */}
                                                <div className="mt-4 p-4 rounded-xl bg-gradient-to-r from-purple-500/10 to-indigo-500/10 border border-purple-500/20">
                                                    <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                                                        <BarChart3 className="w-4 h-4 text-purple-400" />
                                                        Monte Carlo Simulation
                                                    </h4>
                                                    <p className="text-xs text-dark-400 mb-3">
                                                        Run 1,000+ simulations to analyze valuation probability distribution
                                                    </p>

                                                    {!monteCarloResults ? (
                                                        <button
                                                            onClick={async () => {
                                                                setIsRunningMonteCarlo(true);
                                                                try {
                                                                    const results = await runMonteCarloSimulation(jobStatus.job_id, 1000);
                                                                    setMonteCarloResults(results);
                                                                } catch (err) {
                                                                    alert("Monte Carlo simulation failed. Please try again.");
                                                                } finally {
                                                                    setIsRunningMonteCarlo(false);
                                                                }
                                                            }}
                                                            disabled={isRunningMonteCarlo}
                                                            className="btn-primary w-full inline-flex items-center justify-center gap-2"
                                                        >
                                                            {isRunningMonteCarlo ? (
                                                                <>
                                                                    <Loader2 className="w-4 h-4 animate-spin" />
                                                                    Running Simulation...
                                                                </>
                                                            ) : (
                                                                <>
                                                                    <BarChart3 className="w-4 h-4" />
                                                                    Run Monte Carlo (1,000 iterations)
                                                                </>
                                                            )}
                                                        </button>
                                                    ) : (
                                                        <div className="space-y-3">
                                                            {/* Results Header */}
                                                            <div className="flex items-center justify-between">
                                                                <span className="text-sm text-green-400 flex items-center gap-1">
                                                                    <CheckCircle className="w-4 h-4" />
                                                                    {monteCarloResults.simulations.toLocaleString()} simulations complete
                                                                </span>
                                                                <button
                                                                    onClick={() => setMonteCarloResults(null)}
                                                                    className="text-xs text-dark-400 hover:text-white"
                                                                >
                                                                    Run Again
                                                                </button>
                                                            </div>

                                                            {/* Statistics Grid */}
                                                            <div className="grid grid-cols-2 gap-2">
                                                                <div className="p-2 rounded-lg bg-dark-800/50">
                                                                    <p className="text-xs text-dark-400">Mean</p>
                                                                    <p className="text-sm font-semibold text-white">
                                                                        ₹{monteCarloResults.results.share_price?.mean?.toFixed(2) || 'N/A'}
                                                                    </p>
                                                                </div>
                                                                <div className="p-2 rounded-lg bg-dark-800/50">
                                                                    <p className="text-xs text-dark-400">Median</p>
                                                                    <p className="text-sm font-semibold text-white">
                                                                        ₹{monteCarloResults.results.share_price?.median?.toFixed(2) || 'N/A'}
                                                                    </p>
                                                                </div>
                                                                <div className="p-2 rounded-lg bg-dark-800/50">
                                                                    <p className="text-xs text-dark-400">5th Percentile</p>
                                                                    <p className="text-sm font-semibold text-red-400">
                                                                        ₹{monteCarloResults.results.share_price?.percentile_5?.toFixed(2) || 'N/A'}
                                                                    </p>
                                                                </div>
                                                                <div className="p-2 rounded-lg bg-dark-800/50">
                                                                    <p className="text-xs text-dark-400">95th Percentile</p>
                                                                    <p className="text-sm font-semibold text-green-400">
                                                                        ₹{monteCarloResults.results.share_price?.percentile_95?.toFixed(2) || 'N/A'}
                                                                    </p>
                                                                </div>
                                                            </div>

                                                            {/* Probability Info */}
                                                            {monteCarloResults.results.probability_above_current !== undefined && (
                                                                <div className="p-2 rounded-lg bg-green-500/10 border border-green-500/20">
                                                                    <p className="text-xs text-dark-400">Probability Above Current Price</p>
                                                                    <p className="text-sm font-semibold text-green-400">
                                                                        {monteCarloResults.results.probability_above_current.toFixed(1)}%
                                                                    </p>
                                                                </div>
                                                            )}

                                                            {/* Confidence Interval */}
                                                            {monteCarloResults.results.confidence_interval_90 && (
                                                                <div className="p-2 rounded-lg bg-purple-500/10 border border-purple-500/20">
                                                                    <p className="text-xs text-dark-400">90% Confidence Interval</p>
                                                                    <p className="text-sm font-semibold text-purple-400">
                                                                        ₹{monteCarloResults.results.confidence_interval_90[0]?.toFixed(2)} - ₹{monteCarloResults.results.confidence_interval_90[1]?.toFixed(2)}
                                                                    </p>
                                                                </div>
                                                            )}
                                                        </div>
                                                    )}
                                                </div>

                                                {/* ========== SENSITIVITY TORNADO CHART ========== */}
                                                <div className="mt-4 p-4 rounded-xl bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/20">
                                                    <div className="flex items-center justify-between mb-3">
                                                        <h4 className="font-medium text-white flex items-center gap-2">
                                                            <BarChart3 className="w-4 h-4 text-orange-400" />
                                                            Sensitivity Analysis
                                                        </h4>
                                                        <button
                                                            onClick={fetchSensitivity}
                                                            className="text-xs px-2 py-1 rounded bg-orange-500/20 text-orange-300 hover:bg-orange-500/30"
                                                        >
                                                            {sensitivityData ? "Refresh" : "Load"}
                                                        </button>
                                                    </div>

                                                    {sensitivityData?.tornado_data ? (
                                                        <div className="space-y-2">
                                                            {sensitivityData.tornado_data.slice(0, 5).map((item: any, i: number) => (
                                                                <div key={i} className="relative">
                                                                    <div className="flex items-center justify-between text-xs mb-1">
                                                                        <span className="text-dark-400">{item.name}</span>
                                                                        <span className="text-dark-300">₹{item.low} - ₹{item.high}</span>
                                                                    </div>
                                                                    <div className="h-4 bg-dark-800 rounded-full overflow-hidden relative">
                                                                        <div
                                                                            className="absolute h-full bg-gradient-to-r from-red-500 to-green-500 rounded-full"
                                                                            style={{
                                                                                left: `${Math.max(0, 50 + (item.low_delta / item.base) * 100)}%`,
                                                                                width: `${Math.min(100, Math.abs(item.range / item.base) * 100)}%`
                                                                            }}
                                                                        />
                                                                        <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-white/50" />
                                                                    </div>
                                                                </div>
                                                            ))}
                                                            <p className="text-xs text-dark-400 text-center mt-2">
                                                                Base: ₹{sensitivityData.base_share_price?.toFixed(2)}
                                                            </p>
                                                        </div>
                                                    ) : (
                                                        <p className="text-xs text-dark-400">
                                                            Click "Load" to see how each assumption impacts valuation
                                                        </p>
                                                    )}
                                                </div>

                                                {/* ========== FOOTBALL FIELD CHART ========== */}
                                                <div className="mt-4 p-4 rounded-xl bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/20">
                                                    <div className="flex items-center justify-between mb-3">
                                                        <h4 className="font-medium text-white flex items-center gap-2">
                                                            <LineChart className="w-4 h-4 text-blue-400" />
                                                            Valuation Summary (Football Field)
                                                        </h4>
                                                        <button
                                                            onClick={fetchFootballField}
                                                            className="text-xs px-2 py-1 rounded bg-blue-500/20 text-blue-300 hover:bg-blue-500/30"
                                                        >
                                                            {footballFieldData ? "Refresh" : "Load"}
                                                        </button>
                                                    </div>

                                                    {footballFieldData?.ranges ? (
                                                        <div className="space-y-3">
                                                            {footballFieldData.ranges.map((range: any, i: number) => (
                                                                <div key={i}>
                                                                    <div className="flex justify-between text-xs text-dark-400 mb-1">
                                                                        <span>{range.method}</span>
                                                                        <span>₹{range.low} - ₹{range.high}</span>
                                                                    </div>
                                                                    <div className="h-5 bg-dark-800 rounded relative overflow-hidden">
                                                                        <div
                                                                            className="absolute h-full rounded"
                                                                            style={{
                                                                                backgroundColor: range.color,
                                                                                left: `${((range.low - footballFieldData.chart_config.min_x) / (footballFieldData.chart_config.max_x - footballFieldData.chart_config.min_x)) * 100}%`,
                                                                                width: `${((range.high - range.low) / (footballFieldData.chart_config.max_x - footballFieldData.chart_config.min_x)) * 100}%`,
                                                                                opacity: range.confidence === "high" ? 1 : 0.6
                                                                            }}
                                                                        />
                                                                    </div>
                                                                </div>
                                                            ))}
                                                            {/* Current Price Line & Summary */}
                                                            <div className="mt-4 p-3 rounded-lg" style={{ backgroundColor: footballFieldData.summary.rating_color + "20" }}>
                                                                <div className="flex items-center justify-between">
                                                                    <div>
                                                                        <p className="text-xs text-dark-400">Target Price</p>
                                                                        <p className="text-lg font-bold text-white">₹{footballFieldData.summary.target_price?.toFixed(2)}</p>
                                                                    </div>
                                                                    <div className="text-right">
                                                                        <p className="text-xs text-dark-400">Upside</p>
                                                                        <p className="text-lg font-bold" style={{ color: footballFieldData.summary.rating_color }}>
                                                                            {footballFieldData.summary.upside_potential?.toFixed(1)}%
                                                                        </p>
                                                                    </div>
                                                                    <div className="px-3 py-1 rounded-full text-sm font-medium" style={{ backgroundColor: footballFieldData.summary.rating_color, color: "white" }}>
                                                                        {footballFieldData.summary.rating}
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    ) : (
                                                        <p className="text-xs text-dark-400">
                                                            Load to see valuation ranges from multiple methods
                                                        </p>
                                                    )}
                                                </div>

                                                {/* ========== AI CHAT BUTTON ========== */}
                                                <button
                                                    onClick={() => setShowChat(!showChat)}
                                                    className="mt-4 w-full p-3 rounded-xl bg-gradient-to-r from-pink-500/20 to-violet-500/20 border border-pink-500/30 hover:border-pink-400/50 transition-all flex items-center justify-center gap-2"
                                                >
                                                    <Sparkles className="w-5 h-5 text-pink-400" />
                                                    <span className="text-white font-medium">Ask AI About This Model</span>
                                                </button>

                                                {jobStatus.validation && (
                                                    <div className="mt-4 p-4 rounded-lg bg-dark-800/50">
                                                        <div className="flex items-center gap-2 mb-2">
                                                            {jobStatus.validation.is_valid ? (
                                                                <CheckCircle className="w-4 h-4 text-green-400" />
                                                            ) : (
                                                                <AlertCircle className="w-4 h-4 text-yellow-400" />
                                                            )}
                                                            <span className="text-sm font-medium text-white">
                                                                Model Validation
                                                            </span>
                                                        </div>
                                                        {jobStatus.validation.errors.length > 0 && (
                                                            <ul className="text-sm text-dark-400 space-y-1">
                                                                {jobStatus.validation.errors.slice(0, 3).map((err, i) => (
                                                                    <li key={i}>• {err.message}</li>
                                                                ))}
                                                            </ul>
                                                        )}
                                                    </div>
                                                )}
                                            </motion.div>
                                        )}

                                        {/* New model button */}
                                        {(jobStatus.status === "completed" || jobStatus.status === "failed") && (
                                            <button
                                                onClick={() => {
                                                    setJobStatus(null);
                                                    setSelectedStock(null);
                                                    setExcelFile(null);
                                                    setExcelCompanyName("");
                                                    setMonteCarloResults(null);
                                                }}
                                                className="btn-secondary w-full mt-2"
                                            >
                                                Generate Another Model
                                            </button>
                                        )}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </motion.div>
                </div>

                {/* Footer */}
                <motion.footer
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                    className="text-center text-dark-500 text-sm mt-8"
                >
                    <p className="flex items-center justify-center gap-2">
                        <LineChart className="w-4 h-4" />
                        Built with AI • DCF Valuation • Charts & Sensitivity Analysis • 150+ Stocks
                    </p>
                </motion.footer>
            </div >

            {/* ========== FLOATING AI CHAT WIDGET ========== */}
            <AnimatePresence>
                {showChat && (
                    <motion.div
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 20, scale: 0.95 }}
                        className="fixed bottom-6 right-6 w-96 max-h-[500px] bg-dark-900 border border-dark-700 rounded-2xl shadow-2xl flex flex-col z-50"
                    >
                        {/* Chat Header */}
                        <div className="flex items-center justify-between p-4 border-b border-dark-700">
                            <div className="flex items-center gap-2">
                                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-pink-500 to-violet-500 flex items-center justify-center">
                                    <Sparkles className="w-4 h-4 text-white" />
                                </div>
                                <div>
                                    <p className="font-medium text-white text-sm">AI Financial Analyst</p>
                                    <p className="text-xs text-dark-400">Ask about {jobStatus?.company_name || "the model"}</p>
                                </div>
                            </div>
                            <button onClick={() => setShowChat(false)} className="text-dark-400 hover:text-white">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Chat Messages */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-3 max-h-72">
                            {chatHistory.length === 0 && (
                                <div className="text-center py-8">
                                    <Sparkles className="w-8 h-8 text-pink-400 mx-auto mb-2" />
                                    <p className="text-sm text-dark-400">Ask me anything about the valuation...</p>
                                    <div className="mt-3 space-y-2">
                                        {["What drives the valuation?", "What are the key risks?", "How sensitive is WACC?"].map((q, i) => (
                                            <button
                                                key={i}
                                                onClick={() => { setChatMessage(q); }}
                                                className="block w-full text-xs text-left px-3 py-2 rounded-lg bg-dark-800 hover:bg-dark-700 text-dark-300"
                                            >
                                                {q}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            )}
                            {chatHistory.map((msg, i) => (
                                <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                                    <div className={`max-w-[80%] px-3 py-2 rounded-xl text-sm ${msg.role === "user"
                                        ? "bg-primary-500 text-white"
                                        : "bg-dark-800 text-dark-200"
                                        }`}>
                                        {msg.content}
                                    </div>
                                </div>
                            ))}
                            {isChatting && (
                                <div className="flex justify-start">
                                    <div className="bg-dark-800 px-3 py-2 rounded-xl">
                                        <Loader2 className="w-4 h-4 animate-spin text-pink-400" />
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Chat Input */}
                        <div className="p-3 border-t border-dark-700">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={chatMessage}
                                    onChange={(e) => setChatMessage(e.target.value)}
                                    onKeyDown={(e) => e.key === "Enter" && sendChatMessage()}
                                    placeholder="Ask about the model..."
                                    className="flex-1 px-3 py-2 rounded-lg bg-dark-800 border border-dark-700 text-white text-sm focus:outline-none focus:border-pink-500"
                                />
                                <button
                                    onClick={sendChatMessage}
                                    disabled={isChatting || !chatMessage.trim()}
                                    className="px-4 py-2 rounded-lg bg-gradient-to-r from-pink-500 to-violet-500 text-white text-sm font-medium disabled:opacity-50"
                                >
                                    Send
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* ========== SAVE PROJECT MODAL ========== */}
            <AnimatePresence>
                {showSaveModal && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="bg-dark-900 border border-dark-700 p-6 rounded-2xl w-full max-w-md shadow-2xl"
                        >
                            <h3 className="text-xl font-bold text-white mb-4">Save Project</h3>
                            <input
                                type="text"
                                placeholder="Project Name"
                                value={projectName}
                                onChange={(e) => setProjectName(e.target.value)}
                                className="input-field w-full mb-4"
                            />
                            <div className="flex justify-end gap-3">
                                <button
                                    onClick={() => setShowSaveModal(false)}
                                    className="px-4 py-2 rounded-lg text-dark-300 hover:text-white"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={saveProject}
                                    className="px-4 py-2 rounded-lg bg-primary-500 text-white hover:bg-primary-600 font-medium"
                                >
                                    Save
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* ========== LOAD PROJECT MODAL ========== */}
            <AnimatePresence>
                {showLoadModal && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="bg-dark-900 border border-dark-700 p-6 rounded-2xl w-full max-w-lg shadow-2xl max-h-[80vh] flex flex-col"
                        >
                            <div className="flex justify-between items-center mb-4">
                                <h3 className="text-xl font-bold text-white">Load Project</h3>
                                <button onClick={() => setShowLoadModal(false)}>
                                    <X className="w-5 h-5 text-dark-400 hover:text-white" />
                                </button>
                            </div>

                            <div className="flex-1 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                                {savedProjects.length === 0 ? (
                                    <p className="text-dark-400 text-center py-8">No saved projects found.</p>
                                ) : (
                                    savedProjects.map((p) => (
                                        <button
                                            key={p.id}
                                            onClick={() => loadProject(p)}
                                            className="w-full text-left p-3 rounded-xl bg-dark-800 hover:bg-dark-700 border border-dark-700 transition-colors group"
                                        >
                                            <p className="font-medium text-white group-hover:text-primary-400 transition-colors">{p.name}</p>
                                            <p className="text-xs text-dark-400 mt-1">
                                                {new Date(p.updated_at).toLocaleDateString()} • {p.project_type || "General"}
                                            </p>
                                        </button>
                                    ))
                                )}
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </main >
    );
}

