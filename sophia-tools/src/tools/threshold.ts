import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface ThresholdInput {
    workspace_root: string;
    proposed_change: string;
    target?: string;
    scope?: string;
}

export interface ReadinessSignal {
    factor: string;
    status: string;
    reason: string;
    weight: number;
}

export interface ThresholdResult {
    proposed_change: string;
    verdict: string;
    readiness_score: number;
    recommendation: string;
    signals: ReadinessSignal[];
    timing_assessment: string;
    entropy_projection: string;
}

export class ThresholdTool implements vscode.LanguageModelTool<ThresholdInput> {
    public readonly name = 'sophia_threshold';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<ThresholdInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { workspace_root, proposed_change, target, scope = 'major' } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/threshold_bridge.py');
            const args = [pythonScript, workspace_root, proposed_change];
            
            if (target) args.push('--target', target);
            args.push('--scope', scope);
            
            const { stdout, stderr } = await execFileAsync('python3', args);

            if (stderr) {
                console.error('Threshold stderr:', stderr);
            }

            const result: ThresholdResult = JSON.parse(stdout);

            return {
                content: [
                    new vscode.LanguageModelTextPart(JSON.stringify(result, null, 2))
                ]
            };
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            return {
                content: [
                    new vscode.LanguageModelTextPart(
                        JSON.stringify({ error: `Threshold failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<ThresholdInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: `Assessing readiness: ${options.input.proposed_change}`
        };
    }
}
