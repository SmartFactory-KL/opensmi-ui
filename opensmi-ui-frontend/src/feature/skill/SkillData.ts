import {
  CircleCheck,
  CirclePause,
  CirclePlay,
  CircleStop,
  LoaderCircle,
  RotateCcw,
  StopCircleIcon,
  Timer,
  type LucideIcon,
} from "@lucide/vue";

export const SkillState = {
  HALTED: 11,
  READY: 12,
  RUNNING: 13,
  SUSPENDED: 14,
  COMPLETED: 15,
  STARTING: 16,
  HALTING: 17,
  COMPLETING: 18,
  RESETTING: 19,
  SUSPENDING: 20,
} as const;

export type StateConfig = {
  label: string;
  description: string;
  icon: LucideIcon;
  color: string;
  iconColor: string;
  barColor: string;
  isBusy: boolean;
};

export const SkillControlLabels: Record<string, number> = {
  halted: SkillState.HALTED,
  ready: SkillState.READY,
  running: SkillState.RUNNING,
  suspended: SkillState.SUSPENDED,
  completed: SkillState.COMPLETED,
  starting: SkillState.STARTING,
  halting: SkillState.HALTING,
  completing: SkillState.COMPLETING,
  resetting: SkillState.RESETTING,
  suspending: SkillState.SUSPENDING,
};

export function normalizeSkillState(
  state: string | number,
): StateConfig | null {
  if (typeof state === "number") {
    return SkillControlStateStyles[state] ?? null;
  }

  if (typeof state !== "string") {
    return null;
  }

  const numericValue = Number(state);
  if (Number.isInteger(numericValue)) {
    return SkillControlStateStyles[numericValue] ?? null;
  }

  const normalized = state.trim().toLowerCase();
  if (normalized === "") {
    return null;
  }

  const stateEnum = SkillControlLabels[normalized] ?? null;
  if (stateEnum === null) {
    return null;
  }

  return SkillControlStateStyles[stateEnum] ?? null;
}

export const SkillControlStateStyles: Record<number, StateConfig> = {
  [SkillState.HALTED]: {
    label: "Halted",
    description: "Stopped · Reset required",
    icon: StopCircleIcon,
    color: "bg-red-50 text-red-800 border-red-200",
    iconColor: "text-red-600",
    barColor: "bg-red-500",
    isBusy: false,
  },
  [SkillState.READY]: {
    label: "Ready",
    description: "Ready to start",
    icon: CircleCheck,
    color: "bg-violet-50 text-violet-800 border-violet-200",
    iconColor: "text-violet-600",
    barColor: "bg-violet-500",
    isBusy: false,
  },
  [SkillState.RUNNING]: {
    label: "Running",
    description: "Execution in progress",
    icon: CirclePlay,
    color: "bg-blue-50 text-blue-800 border-blue-200",
    iconColor: "text-blue-600",
    barColor: "bg-blue-500",
    isBusy: true,
  },
  [SkillState.SUSPENDED]: {
    label: "Suspended",
    description: "Execution paused",
    icon: CirclePause,
    color: "bg-amber-50 text-amber-800 border-amber-200",
    iconColor: "text-amber-600",
    barColor: "bg-amber-500",
    isBusy: false,
  },
  [SkillState.COMPLETED]: {
    label: "Completed",
    description: "Execution completed",
    icon: CircleCheck,
    color: "bg-teal-50 text-teal-800 border-teal-200",
    iconColor: "text-teal-600",
    barColor: "bg-teal-500",
    isBusy: false,
  },
  [SkillState.STARTING]: {
    label: "Starting",
    description: "Transitioning to running",
    icon: LoaderCircle,
    color: "bg-sky-50 text-sky-800 border-sky-200",
    iconColor: "text-sky-600",
    barColor: "bg-sky-500",
    isBusy: true,
  },
  [SkillState.HALTING]: {
    label: "Halting",
    description: "Transitioning to halted",
    icon: CircleStop,
    color: "bg-orange-50 text-orange-800 border-orange-200",
    iconColor: "text-orange-600",
    barColor: "bg-orange-500",
    isBusy: true,
  },
  [SkillState.COMPLETING]: {
    label: "Completing",
    description: "Finishing execution",
    icon: CircleCheck,
    color: "bg-teal-50 text-teal-800 border-teal-200",
    iconColor: "text-teal-600",
    barColor: "bg-teal-500",
    isBusy: true,
  },
  [SkillState.RESETTING]: {
    label: "Resetting",
    description: "Returning to ready",
    icon: RotateCcw,
    color: "bg-violet-50 text-violet-800 border-violet-200",
    iconColor: "text-violet-600",
    barColor: "bg-violet-500",
    isBusy: true,
  },
  [SkillState.SUSPENDING]: {
    label: "Suspending",
    description: "Transitioning to suspended",
    icon: Timer,
    color: "bg-amber-50 text-amber-800 border-amber-200",
    iconColor: "text-amber-600",
    barColor: "bg-amber-500",
    isBusy: true,
  },
};
