"""add update_user_balance function

Revision ID: add_update_balance
Revises: 7c6142541c8f
Create Date: 2025-12-17 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_update_balance'
down_revision: Union[str, None] = '7c6142541c8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the update_user_balance PostgreSQL function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_user_balance(p_user_id INTEGER)
        RETURNS JSON AS $$
        DECLARE
            v_old_balance DECIMAL(15, 2);
            v_new_balance DECIMAL(15, 2);
            v_balance_increase DECIMAL(15, 2);
            v_result JSON;
        BEGIN
            -- Get current balance
            SELECT balance INTO v_old_balance
            FROM users
            WHERE id = p_user_id;
            
            IF v_old_balance IS NULL THEN
                RAISE EXCEPTION 'User with id % not found', p_user_id;
            END IF;
            
            -- Calculate balance increase (example: add sum of completed transactions)
            -- This is a placeholder - adjust logic as needed
            SELECT COALESCE(SUM(
                CASE WHEN is_withdraw THEN -amount ELSE amount END
            ), 0) INTO v_balance_increase
            FROM transactions
            WHERE user_id = p_user_id
            AND created_at > (SELECT balance_updated_at FROM users WHERE id = p_user_id);
            
            -- Update user balance
            v_new_balance := v_old_balance + v_balance_increase;
            
            UPDATE users
            SET balance = v_new_balance,
                balance_updated_at = NOW()
            WHERE id = p_user_id;
            
            -- Return JSON result
            v_result := json_build_object(
                'balance_increase', v_balance_increase,
                'new_balance', v_new_balance
            );
            
            RETURN v_result;
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS update_user_balance(INTEGER);")
