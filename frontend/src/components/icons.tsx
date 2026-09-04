type P = { className?: string };
const D = "h-[17px] w-[17px]";
const s = { fill: "none", stroke: "currentColor", strokeWidth: 1.6, strokeLinecap: "round", strokeLinejoin: "round" } as const;

export const GridIcon = ({ className = D }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}>
    <rect x="3.5" y="3.5" width="7" height="7" rx="1.8" /><rect x="13.5" y="3.5" width="7" height="7" rx="1.8" />
    <rect x="3.5" y="13.5" width="7" height="7" rx="1.8" /><rect x="13.5" y="13.5" width="7" height="7" rx="1.8" />
  </svg>
);

export const RadarIcon = ({ className = D }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}>
    <circle cx="12" cy="12" r="8.5" /><circle cx="12" cy="12" r="4" /><path d="M12 12 18.2 5.8" />
  </svg>
);

export const CalendarIcon = ({ className = D }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}>
    <rect x="3.5" y="5" width="17" height="15.5" rx="2.5" /><path d="M3.5 9.5h17M8 3.5v3M16 3.5v3" />
  </svg>
);

export const FileIcon = ({ className = D }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}>
    <path d="M13.5 3H7a1.8 1.8 0 0 0-1.8 1.8v14.4A1.8 1.8 0 0 0 7 21h10a1.8 1.8 0 0 0 1.8-1.8V8.2Z" /><path d="M13.5 3v5.2h5.3" />
  </svg>
);

export const JournalIcon = ({ className = D }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}>
    <path d="M5 4.8h11.2A1.8 1.8 0 0 1 18 6.6v12.6H6.8A1.8 1.8 0 0 1 5 17.4Z" /><path d="M8.6 9h6M8.6 12.4h6M8.6 15.8h3.4" />
  </svg>
);

export const SearchIcon = ({ className = "h-4 w-4" }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}><circle cx="11" cy="11" r="6.6" /><path d="m16.2 16.2 3.8 3.8" /></svg>
);

export const BellIcon = ({ className = "h-[18px] w-[18px]" }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}>
    <path d="M18 15.5V10a6 6 0 1 0-12 0v5.5L4.5 18h15Z" /><path d="M10 21h4" />
  </svg>
);

export const PlusIcon = ({ className = "h-4 w-4" }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}><path d="M12 5.5v13M5.5 12h13" /></svg>
);

export const DownloadIcon = ({ className = "h-4 w-4" }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}><path d="M12 4v11m0 0 4.5-4.5M12 15l-4.5-4.5M5 19h14" /></svg>
);

export const CaretIcon = ({ className = "h-3.5 w-3.5" }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}><path d="m6.5 9.5 5.5 5.5 5.5-5.5" /></svg>
);

export const ChevronIcon = ({ className = "h-4 w-4" }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}><path d="m9 5 7 7-7 7" /></svg>
);

export const ShareIcon = ({ className = "h-[15px] w-[15px]" }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}>
    <circle cx="17.5" cy="6" r="2.6" /><circle cx="6.5" cy="12" r="2.6" /><circle cx="17.5" cy="18" r="2.6" />
    <path d="m9 10.7 6-3.4M9 13.3l6 3.4" />
  </svg>
);

export const ClockIcon = ({ className = "h-[15px] w-[15px]" }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}><circle cx="12" cy="12" r="8.4" /><path d="M12 7.4V12l3.1 2" /></svg>
);

export const CheckCircleIcon = ({ className = "h-[15px] w-[15px]" }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}><circle cx="12" cy="12" r="8.4" /><path d="m8.4 12.2 2.4 2.4 4.6-4.8" /></svg>
);

export const RupeeIcon = ({ className = "h-[15px] w-[15px]" }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}><path d="M7.5 5.5h9M7.5 9.5h9M14.5 5.5c2.4 0 3.6 1.4 3.6 3.4 0 2.6-2 3.9-4.6 3.9H9.4l7 6.2" /></svg>
);

export const ListIcon = ({ className = "h-[16px] w-[16px]" }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}><path d="M8.5 6.5h11M8.5 12h11M8.5 17.5h11M4.5 6.5h.01M4.5 12h.01M4.5 17.5h.01" /></svg>
);

export const SettingsIcon = ({ className = D }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}>
    <circle cx="12" cy="12" r="2.9" />
    <path d="M19.2 14.2a1.5 1.5 0 0 0 .3 1.7l.1.1a1.8 1.8 0 1 1-2.6 2.6l-.1-.1a1.5 1.5 0 0 0-2.6 1.1v.2a1.8 1.8 0 1 1-3.6 0v-.1a1.5 1.5 0 0 0-2.6-1.1l-.1.1a1.8 1.8 0 1 1-2.6-2.6l.1-.1a1.5 1.5 0 0 0-1.1-2.6h-.2a1.8 1.8 0 1 1 0-3.6h.1a1.5 1.5 0 0 0 1.1-2.6l-.1-.1a1.8 1.8 0 1 1 2.6-2.6l.1.1a1.5 1.5 0 0 0 2.6-1.1v-.2a1.8 1.8 0 1 1 3.6 0v.1a1.5 1.5 0 0 0 2.6 1.1l.1-.1a1.8 1.8 0 1 1 2.6 2.6l-.1.1a1.5 1.5 0 0 0 1.1 2.6h.2a1.8 1.8 0 1 1 0 3.6h-.1a1.5 1.5 0 0 0-1.4.9Z" />
  </svg>
);

export const HelpIcon = ({ className = D }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}>
    <circle cx="12" cy="12" r="8.6" /><path d="M9.7 9.6a2.4 2.4 0 1 1 3.2 2.3c-.6.2-.9.8-.9 1.4v.4M12 16.6h.01" />
  </svg>
);

export const QuoteIcon = ({ className = "h-3 w-3" }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}><path d="M6 6.5h12M6 11h12M6 15.5h8" /></svg>
);

export const AlertIcon = ({ className = D }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}>
    <path d="M12 4.2 21 19.5H3Z" /><path d="M12 10v4M12 16.8h.01" />
  </svg>
);

export const CogIcon = ({ className = D }: P) => (
  <svg className={className} viewBox="0 0 24 24" {...s}>
    <circle cx="12" cy="12" r="3" />
    <path d="M12 3.5v2.2M12 18.3v2.2M20.5 12h-2.2M5.7 12H3.5M18 6l-1.6 1.6M7.6 16.4 6 18M18 18l-1.6-1.6M7.6 7.6 6 6" />
  </svg>
);
