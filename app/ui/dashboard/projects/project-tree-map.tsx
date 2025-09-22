import { ResponsiveTreeMap } from '@nivo/treemap'

import { TreeNode } from '@/app/lib/definitions';

const MyResponsiveTreeMap = ({ data }: { data: TreeNode }) => (
    <ResponsiveTreeMap
        data={data}
        identity="name"
        value="loc"
        tile="squarify"
        leavesOnly={false}
        colors={{ scheme: 'yellow_orange_red' }}
        valueFormat=".02s"
        margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
        labelSkipSize={12}
        labelTextColor={{
            from: 'color',
            modifiers: [
                [
                    'darker',
                    1.2
                ]
            ]
        }}
        parentLabel={(node) => `${node.id} (${node.value})`}
        parentLabelPosition="top"
        parentLabelTextColor={{
            from: 'color',
            modifiers: [
                [
                    'darker',
                    2
                ]
            ]
        }}
        borderColor={{
            from: 'color',
            modifiers: [
                [
                    'darker',
                    0.1
                ]
            ]
        }}
        motionConfig="slow"
    />
)

export default MyResponsiveTreeMap;