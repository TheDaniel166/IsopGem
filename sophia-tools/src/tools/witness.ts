import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface WitnessInput {
    workspace_root: string;
    action: string;
    target?: string;
    decision?: string;
    intent?: string;
    tradeoffs?: string;
    alternatives?: string;
}

export interface IntentArtifact {
    id: string;
    timestamp: string;
    decision: string;
    intent: string;
    context: string;
    tradeoffs: string[];
    alternatives_rejected: Array<{alternative: string; reason: string}>;
    affected_structures: string[];
    preservation_reason: string;
}

export interface WitnessResult {
    action: string;
    artifacts?: IntentArtifact[];
    recorded?: IntentArtifact;
    message: string;
}

export class WitnessTool implements vscode.LanguageModelTool<WitnessInput> {
    public readonly name = 'sophia_witness';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<WitnessInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { 
            workspace_root, 
            action, 
            target, 
            decision, 
            intent, 
            tradeoffs, 
            alternatives 
        } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/witness_bridge.py');
            const args = [pythonScript, workspace_root, action];
            
            if (target) args.push('--target', target);
            if (decision) args.push('--decision', decision);
            if (intent) args.push('--intent', intent);
            if (tradeoffs) args.push('--tradeoffs', tradeoffs);
            if (alternatives) args.push('--alternatives', alternatives);
            
            const { stdout, stderr } = await execFileAsync('python3', args);

            if (stderr) {
                console.error('Witness stderr:', stderr);
            }

            const result: WitnessResult = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Witness failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<WitnessInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        const actionDesc = options.input.action === 'record' ? 'Recording intent' : 'Querying intent';
        return {
            invocationMessage: `${actionDesc}: ${options.input.target || 'architectural decision'}`
        };
    }
}
