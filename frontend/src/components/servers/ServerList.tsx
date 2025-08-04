import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Box,
  Button,
  Chip,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Tooltip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  CheckCircle as OnlineIcon,
  Cancel as OfflineIcon,
} from '@mui/icons-material';
import serverService, { ServerListItem } from '../../services/serverService';

const ServerList: React.FC = () => {
  const [servers, setServers] = useState<ServerListItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshingIds, setRefreshingIds] = useState<number[]>([]);

  const fetchServers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await serverService.getServers();
      setServers(data);
    } catch (err) {
      console.error('Error fetching servers:', err);
      setError('Failed to load servers. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServers();
  }, []);

  const handleRefreshStatus = async (id: number) => {
    setRefreshingIds((prev) => [...prev, id]);
    try {
      const updatedServer = await serverService.checkServerStatus(id);
      setServers((prev) =>
        prev.map((server) =>
          server.id === id
            ? {
                ...server,
                status: updatedServer.status,
              }
            : server
        )
      );
    } catch (err) {
      console.error(`Error refreshing server ${id} status:`, err);
    } finally {
      setRefreshingIds((prev) => prev.filter((serverId) => serverId !== id));
    }
  };

  const handleDeleteServer = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this server?')) {
      try {
        await serverService.deleteServer(id);
        setServers((prev) => prev.filter((server) => server.id !== id));
      } catch (err) {
        console.error(`Error deleting server ${id}:`, err);
        alert('Failed to delete server. Please try again.');
      }
    }
  };

  if (loading && servers.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" component="h1">
          Servers
        </Typography>
        <Button
          component={Link}
          to="/servers/new"
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
        >
          Add Server
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {servers.length === 0 && !loading ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" color="textSecondary">
            No servers found. Click "Add Server" to create your first server.
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>IP Address</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Tags</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {servers.map((server) => (
                <TableRow key={server.id}>
                  <TableCell component="th" scope="row">
                    <Link to={`/servers/${server.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                      <Typography variant="body1" fontWeight="medium">
                        {server.name}
                      </Typography>
                    </Link>
                  </TableCell>
                  <TableCell>{server.ip_address}</TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center">
                      {server.status ? (
                        <>
                          {server.status.is_online ? (
                            <Tooltip title="Online">
                              <OnlineIcon color="success" fontSize="small" />
                            </Tooltip>
                          ) : (
                            <Tooltip title={server.status.error_message || 'Offline'}>
                              <OfflineIcon color="error" fontSize="small" />
                            </Tooltip>
                          )}
                          <Box ml={1}>{server.status.is_online ? 'Online' : 'Offline'}</Box>
                        </>
                      ) : (
                        'Unknown'
                      )}
                      <IconButton
                        size="small"
                        onClick={() => handleRefreshStatus(server.id)}
                        disabled={refreshingIds.includes(server.id)}
                        sx={{ ml: 1 }}
                      >
                        {refreshingIds.includes(server.id) ? (
                          <CircularProgress size={20} />
                        ) : (
                          <RefreshIcon fontSize="small" />
                        )}
                      </IconButton>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" flexWrap="wrap" gap={0.5}>
                      {server.tags.map((tag) => (
                        <Chip key={tag} label={tag} size="small" />
                      ))}
                      {server.tags.length === 0 && (
                        <Typography variant="body2" color="textSecondary">
                          No tags
                        </Typography>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="Edit">
                      <IconButton
                        component={Link}
                        to={`/servers/${server.id}/edit`}
                        size="small"
                        sx={{ mr: 1 }}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteServer(server.id)}
                        color="error"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default ServerList;