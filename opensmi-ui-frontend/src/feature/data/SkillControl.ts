import type { SkillControlAction } from "@/types/UpdateTypes";
import {
  ArrowDownLeftFromSquareIcon,
  CircleCheck,
  CirclePause,
  CirclePlay,
  CircleStop,
  LoaderCircle,
  PauseCircleIcon,
  PlayCircleIcon,
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

export const SkillControlControls: {
  action: SkillControlAction["requestedAction"];
  label: string;
  icon: LucideIcon;
  classes: string;
}[] = [
  {
    action: "Reset",
    label: "Reset",
    icon: ArrowDownLeftFromSquareIcon,
    classes:
      "text-violet-600 bg-violet-50 hover:text-violet-700 focus-visible:ring-violet-500",
  },
  {
    action: "Start",
    label: "Start",
    icon: PlayCircleIcon,
    classes:
      "text-emerald-600 bg-emerald-50 hover:text-emerald-700 focus-visible:ring-emerald-500",
  },
  {
    action: "Suspend",
    label: "Suspend",
    icon: PauseCircleIcon,
    classes:
      "text-amber-600 bg-amber-50 hover:text-amber-700 focus-visible:ring-amber-500",
  },
  {
    action: "Halt",
    label: "Halt",
    icon: StopCircleIcon,
    classes:
      "text-red-600 bg-red-50 hover:text-red-700 focus-visible:ring-red-500",
  },
];

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
