'use client';
import { useTranslation } from 'react-i18next';
import {
    CircleIcon,
	DrawingPinFilledIcon,
	DrawingPinIcon,
	OpenInNewWindowIcon,
    MoveIcon,
    DoubleArrowDownIcon,
    ColorWheelIcon,
    EnterIcon,
    DoubleArrowRightIcon,
    AlignBaselineIcon,
    OpacityIcon
} from "@radix-ui/react-icons";
import {
	Badge,
	Box,
	Card,
	Flex,
	Grid,
	Heading,
	IconButton,
	Text,
    BadgeProps,
} from "@radix-ui/themes";
import * as React from "react";
import CardHover from "./helpers/performance-card-helpers";
import { hoverMessages, LayoutProps } from "@/app/lib/definitions";
import Breadcrumbs from '@/app/ui/breadcrumbs';
import { Breadcrumb } from '@/app/lib/definitions';
import { lusitana } from "../../fonts";

const formatValues = (value: number) => {
    // Format value with appropriate suffix for large numbers
    if (value >= 1_000_000) {
        return `${(value / 1_000_000).toFixed(2)}M`;
    } else if (value >= 1_000) {
        return `${(value / 1_000).toFixed(2)}K`;
    } else {
        return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value);
    }
};

export default function PerformanceCard({ data, focusable, ...props }: LayoutProps) {
    const { t } = useTranslation('common');
    const { projectId, projectName, totalImpact, totalInvestment, totalBankableInvestment, totalIncome, landNumber, totalco2, area, averageCo2Total, sumCo2Total } = data;

    const safeDivide = (numerator: number, denominator: number) => {
        return denominator === 0 ? 0 : numerator / denominator;
    };

        const tabIndex = focusable ? undefined : -1;

        const [state, setState] = React.useState({
            todo: [
                { id: "a", completed: false },
                { id: "b", completed: false },
                { id: "c", completed: false },
                { id: "d", completed: false },
                { id: "e", completed: true },
                { id: "f", completed: true },
            ],
            activityPinned: true,
            financePinned: false,
        });


    return (
        <div>
            <Breadcrumbs
                breadcrumbs={[
                { label: t('breadcrumbHome'), href: '/' },
                { label: t('breadcrumbProjects'), href: '/dashboard' },
                projectId ? { label: projectName, href: `/dashboard/project/${projectId}`, active: true } : null
                ].filter((breadcrumb): breadcrumb is Breadcrumb => breadcrumb !== null)}
            />

            <h1 className={`${lusitana.className} mb-6 text-2xl md:text-3xl font-bold text-mint-11 dark:text-mint-9`}>
                {projectId ? projectName : t('breadcrumbProjects')}
            </h1>
        
            <Flex align="center" gap="6" {...props} width="100%">
                <Flex flexShrink="0" gap="6" direction="column" width="100%">
                    <Card size="4" style={{ width: '100%' }}>
                        <Heading as="h3" size="6" trim="start" mb="2">
                            {t('mainIndicators')}
                        </Heading>

                        <Flex position="absolute" top="0" right="0" m="3">
                            <IconButton
                                tabIndex={tabIndex}
                                variant="ghost"
                                color="gray"
                                highContrast
                                style={{ margin: 0 }}
                            >
                                <OpenInNewWindowIcon width="20" height="20" />
                            </IconButton>

                            <IconButton
                                tabIndex={tabIndex}
                                variant={state.financePinned ? "soft" : "ghost"}
                                color="gray"
                                highContrast
                                style={{ margin: 0 }}
                                onClick={() =>
                                    setState((state) => ({
                                        ...state,
                                        financePinned: !state.financePinned,
                                    }))
                                }
                            >
                                {state.financePinned ? (
                                    <DrawingPinFilledIcon width="20" height="20" />
                                ) : (
                                    <DrawingPinIcon width="20" height="20" />
                                )}
                            </IconButton>
                        </Flex>

                        <Text as="p" size="2" mb="6" color="gray">
                            {t('relevantIndicators')}
                        </Text>

                        <Grid columns={{ xs: "2", md: "4" }} gap="3">
                            <Indicator title="Impact" color="amber" icon="move" value={totalImpact} units="TonnesCO2eq" />
                            <Indicator title="Investment" color="gold" icon="doubleArrow" value={totalInvestment} units="USD" />
                            <Indicator title="Bankable" color="tomato" icon="wheel" value={totalBankableInvestment} units="USD" />
                            <Indicator title="Income" color="plum" icon="enter" value={totalIncome} units="USD" />
                            <Indicator title="Lands" color="brown" icon="circle" value={landNumber} />
                            <Indicator title="TotalCO2eq" color="iris" icon="doubleArrowRight" value={totalco2} units="TonnesCO2eq" />
                            <Indicator title="Area" color="teal" icon="alignBaseline" value={area} units="Ha" />
                            <Indicator title="CO2eq" color="amber" icon="move" value={safeDivide(totalco2, area)} units="TonnesCO2eq/Ha" />
                            <Indicator title="Co2eq Year" color="violet" icon="opacity" value={safeDivide(totalco2, area) / 20} units="TonnesCO2eq/Ha/year" />
                            <Indicator title="Area Tokens" color="teal" icon="alignBaseline" value={area} />
                            <Indicator title="Token Value" color="tomato" icon="doubleArrowDownIcon" value={averageCo2Total} units="TonnesCO2eq/Ha" />
                            <Indicator title="Token Value Total" color="mint" icon="doubleArrowRightIcon" value={sumCo2Total} units="TonnesCO2eq" />
                           
                        </Grid>
                    </Card>
                </Flex>
            </Flex>
        </div>
    );
}

const iconMap = {
    move: MoveIcon,
    doubleArrow: DoubleArrowDownIcon,
    wheel: ColorWheelIcon,
    enter: EnterIcon,
    circle: CircleIcon,
    doubleArrowRight: DoubleArrowRightIcon,
    alignBaseline: AlignBaselineIcon,
    opacity: OpacityIcon,
    doubleArrowDownIcon: DoubleArrowDownIcon,
    doubleArrowRightIcon: DoubleArrowRightIcon,

  };

function Indicator({ title, color, icon, value, units }: { 
    title: string, 
    color: BadgeProps['color'],
    icon: keyof typeof iconMap,
    value: number,
    units?: string,
    }
) {
    const { t } = useTranslation('common');
    const Icon = iconMap[icon];
    const hoverMessageKey = title.toLowerCase().replace(/\s+/g, '_');
    const hoverMessage = hoverMessages[hoverMessageKey] || hoverMessages.default;

    return (
        <Box>
            <Flex gap="1" mb="1" align="center">
                <Text size={{ xs: '2', md: '1' }} color="gray">
                    {title}
                </Text>
                {units && (
                    <Text size={{ xs: '2', md: '1' }} color="gray">
                        ({units})
                    </Text>
                )}
                <CardHover 
                    icon={hoverMessage.icon} 
                    message={{
                        // icon: hoverMessage.icon,
                        title: t(`hoverMessages.${hoverMessageKey}.title`),
                        content: t(`hoverMessages.${hoverMessageKey}.content`)
                    }}
                >
                    <Badge color={color} radius="full">
                        <Icon
                            width="12"
                            height="12"
                            style={{ marginLeft: -2 }}
                        />
                    </Badge>
                </CardHover>
            </Flex>
            <Text as="div" mb="1" size={{ xs: '7', md: '8' }} weight="bold">
                {formatValues(value)}
            </Text>
        </Box>
    );
}